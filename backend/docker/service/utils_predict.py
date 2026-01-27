import os
import json
from typing import List, Optional
import pandas as pd
import yaml
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import PandasTools
from rdkit.Chem.Draw import rdMolDraw2D
from matplotlib import colormaps

CUSTOM_PALETTE = {
    7: (0.5, 0, 1),
}

class Draw2DMol:
    def __init__(self, explain_dir, config_path, save_path):
        data_path = os.path.join(explain_dir, "dataset.predict_0.sdf")
        self.df = PandasTools.LoadSDF(data_path, removeHs=False) # type: ignore
        self.df['GROUP_list'] = self.df['GROUP'].apply(lambda x: [int(i) for i in x.split(' ')])
        self.df['GROUP_idx'] = self.df['GROUP_list'].apply(lambda x: x[0])
        self.df = self.df.apply(pd.to_numeric, errors='ignore')

        self.config_path = config_path
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config_dict = yaml.safe_load(f)
            self.target_cols:List[str]= [
                col.strip()
                for col in self.config_dict["Datahub"]["target_cols"].split(",")
            ]
            self.task = self.config_dict["Base"]["task"]

        self.target_col:str = self.target_cols[0]
        if self.task in ['classification', 'multilabel_classification']:
            self.predict_cols: List[str] = ['prob_'+target_col for target_col in self.target_cols]
            self.predict_col = 'prob_' + self.target_col
            
        elif self.task in ['regression', 'multilabel_regression']:
            self.predict_cols = ['predict_'+target_col for target_col in self.target_cols]
            self.predict_col = 'predict_'+self.target_col
        elif self.task == 'multiclass':
            self.predict_cols = [col for col in self.df.columns if col.startswith('prob')]
            self.predict_col = 'prob_'+self.target_col
            self.df[self.predict_col] = self.df[self.predict_cols].max(axis=1)

        self.custom_palette = CUSTOM_PALETTE
        self.save_path = save_path
        os.makedirs(self.save_path, exist_ok=True)

    def set_target(self, target_col:Optional[str]=None, idx:Optional[int]=None):
        if target_col is None and idx is None:
            target_col = self.target_col
        elif target_col is None and idx is not None:
            target_col = self.target_cols[idx]
        else:
            pass
        if target_col not in self.target_cols:
            print(f"target_col {target_col} not in target_cols {self.target_cols}")
            return
        
        self.target_col = target_col
        if self.task in ['classification', 'multilabel_classification', 'multiclass']:
            self.predict_col = 'prob_'+target_col
        elif self.task in ['regression', 'multilabel_regression']:
            self.predict_col = 'predict_'+target_col
    
    def __len__(self):
        return len(self.df['GROUP_idx'].unique())
    
    def get_drawer_by_idx(self, idx):
        temp_df = self.df[self.df['GROUP_idx'] == idx]
        if temp_df.shape[0] == 0:
            return None
        elif temp_df.shape[0] == 1:
            mol = temp_df.iloc[0]['ROMol']
            drawer = self.plot2d(mol)
            drawer.WriteDrawingText(os.path.join(self.save_path, self.target_col, f"plot2D_{idx}.png"))
            return drawer

        diff_value_list = []
        diff_atoms_list = []

        for i in range(1, len(temp_df)):
            diff_value_list.append(temp_df.iloc[0][self.predict_col] - temp_df.iloc[i][self.predict_col])
            diff_atoms_list.append(temp_df.iloc[i]['GROUP_list'][1:])
        mol = temp_df.iloc[0]['ROMol']
        drawer = self.plot2dcolorful(mol, diff_atoms_list, diff_value_list)
        drawer.WriteDrawingText(os.path.join(self.save_path, self.target_col, f"plot2D_{idx}.png"))
        return drawer
    
    def get_all_drawer(self):
        for idx in range(len(self.target_cols)):
            self.set_target(idx=idx)
            os.makedirs(os.path.join(self.save_path, self.target_col), exist_ok=True)
            for i in self.df['GROUP_idx'].unique():
                self.get_drawer_by_idx(i)
    
    def plot2d(self, mol):
        mol_no_h = Chem.RemoveHs(mol)
        AllChem.Compute2DCoords(mol_no_h) # type: ignore
        drawer = rdMolDraw2D.MolDraw2DCairo(600, 600)
        opts = drawer.drawOptions()
        opts.updateAtomPalette(self.custom_palette)
        drawer.DrawMolecule(mol_no_h)
        drawer.FinishDrawing()
        return drawer

    def plot2dcolorful(self, mol, diff_atoms_list, diff_value_list):
        mol_no_h = Chem.RemoveHs(mol)
        AllChem.Compute2DCoords(mol_no_h)
        atom_mapping = self.map_atoms(mol, mol_no_h)
        diff_atoms_list = self.mapping_atoms_list(atom_mapping, diff_atoms_list)

        AllChem.Compute2DCoords(mol) # type: ignore     
        cmap = colormaps['bwr']
        max_abs_value = max(abs(min(diff_value_list)), abs(max(diff_value_list)))
        normalized_values = [x / max_abs_value * 0.4 + 0.6  if x > 0 else x / max_abs_value * 0.4 + 0.4 for x in diff_value_list]
        color_list = [cmap(x) for x in normalized_values]
        
        opts = rdMolDraw2D.MolDrawOptions()
        highlight_atoms = {}
        highlight_atoms.update({k: color_list[i] for i, atoms in enumerate(diff_atoms_list) for k in atoms})
        highlight_atoms.pop(-1, None)
        opts.atomHighlights = highlight_atoms
        opts.updateAtomPalette(self.custom_palette)
        drawer = rdMolDraw2D.MolDraw2DCairo(600, 600)
        drawer.SetDrawOptions(opts)
        drawer.DrawMolecule(mol_no_h, highlightAtoms=highlight_atoms, highlightAtomColors=highlight_atoms)
        drawer.FinishDrawing()
        return drawer
    
    def map_atoms(self, mol, mol_no_h):
        atom_map = {}
        mol_atoms = mol.GetAtoms()
        mol_no_h_atoms = mol_no_h.GetAtoms()
        mol_index = 0
        mol_no_h_index = 0
        while mol_index < len(mol_atoms) and mol_no_h_index < len(mol_no_h_atoms):
            if mol_atoms[mol_index].GetSymbol() != 'H':
                atom_map[mol_index] = mol_no_h_index
                mol_no_h_index += 1
            mol_index += 1
        
        return atom_map
    
    def mapping_atoms_list(self, atom_map, diff_atoms_list):
        return [[atom_map.get(atom, -1) for atom in atoms_list] for atoms_list in diff_atoms_list]

class ChartDataInfer:
    def __init__(self, data_path, config_path, save_dir, smiles_col=None):
        self.df = pd.read_csv(data_path) 
        predict_dir = os.path.dirname(data_path)
        self.phychemprop = pd.read_csv(os.path.join(predict_dir, 'phychemprop.csv'))
        assert len(self.df) == len(self.phychemprop)

        self.config_path = config_path
        self.save_dir = save_dir
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config_dict = yaml.safe_load(f)
            self.target_cols = [
                col.strip()
                for col in self.config_dict["Datahub"]["target_cols"].split(",")
            ]
            self.task = self.config_dict["Base"]["task"]
            self.smiles_col = self.config_dict["Datahub"]["smiles_col"]

        self.custom_palette = CUSTOM_PALETTE

        self.df_clean = self._get_clean_result()
        self.plot2d_all(self.df_clean['SMILES'])


    def _get_clean_result(self):
        smiles_col = self.smiles_col
        predict_cols = ['predict_' + col for col in self.target_cols]
        
        if self.task == 'multiclass':
            uncertain_cols = [col for col in self.df.columns if col.startswith('prob_')]
        elif self.task in ['classification', 'multilabel_classification']:
            uncertain_cols = ['prob_' + col for col in self.target_cols]
        elif self.task in ['regression', 'multilabel_regression']:
            uncertain_cols = ['predict_std_' + col for col in self.target_cols]

        result_cols = [smiles_col] + predict_cols + uncertain_cols
        result = self.df[result_cols]
        result = result.rename(columns={smiles_col: 'SMILES'})
        return result
    
    def plot2d_smiles(self, smiles):
        mol = Chem.MolFromSmiles(smiles)
        AllChem.Compute2DCoords(mol) # type: ignore
        drawer = rdMolDraw2D.MolDraw2DCairo(600, 600)
        opts = drawer.drawOptions()
        opts.updateAtomPalette(self.custom_palette)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        return drawer

    def plot2d_all(self, smiles_list):
        os.makedirs(os.path.join(self.save_dir, 'plot/origin'), exist_ok=True)
        for enu, smiles in enumerate(smiles_list):
            drawer = self.plot2d_smiles(smiles)
            # 图片文件名加origin前缀，为了防止target_cols中存在列名为“origin”
            drawer.WriteDrawingText(os.path.join(self.save_dir, 'plot/origin', f"origin_plot2D_{enu}.png"))
        return None

    def get_result(self, explain_dir=None):
        result_df = pd.concat([self.df_clean, self.phychemprop], axis=1)
        if explain_dir is not None:
            for target_col in self.target_cols:
                result_df['2D_Graph_Explanation_'+target_col] = [os.path.join(explain_dir, target_col, f'plot2D_{i}.png') for i in range(len(result_df))]
        result_df['2D_Graph'] = [os.path.join(self.save_dir, 'plot/origin', f'origin_plot2D_{i}.png') for i in range(len(result_df))]
        result_dict = result_df.to_dict(orient='index')
        os.makedirs(self.save_dir, exist_ok=True)
        with open(os.path.join(self.save_dir, 'result.json'), 'w') as f:
            json.dump(result_dict, f, indent=4)
        return result_dict

if '__main__' == __name__:

    data_basename = 'test'
    save_path = '/vepfs/fs_users/cuiyaning/uni-qsar/0821/optuna-dml/out/hia_hou/'

    config_path = '/vepfs/fs_users/cuiyaning/uni-qsar/0821/optuna-dml/out/hia_hou/config.yaml'

    chart_save_path = '/vepfs/fs_users/cuiyaning/gitlab/qsar_server/hia_hou/chartdata'
    plot_save_path = '/vepfs/fs_users/cuiyaning/gitlab/qsar_server/hia_hou/chartdata/2dplot2'

    data_path = os.path.join(save_path, f'Predict/{data_basename}.predict_0.csv')
    explain_dir = os.path.join(save_path, 'Explain')

    chartdata = ChartDataInfer(data_path, config_path, chart_save_path)
    chartdata.get_result(explain_dir=plot_save_path)

    draw2d = Draw2DMol(explain_dir, config_path, plot_save_path)
    draw2d.get_all_drawer()