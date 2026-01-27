import os
from typing import TypeVar, Generic
from pydantic import BaseModel
import json
import pandas as pd
import numpy as np
from rdkit.Chem import PandasTools
import yaml,logging
from sklearn.metrics import roc_curve, confusion_matrix

logger = logging.getLogger("app")
# raw_files, valid_files
FILES_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/files" 
MODELS_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/models"
# f"{MODELS_DIR}/{experiment.experiment_id}/{run_id}
T = TypeVar('T')

class RES(BaseModel, Generic[T]):
	code: int = 0
	#data: T | None = None
	msg: str = ''

class FrontEndData:
    def __init__(self, model_dir, data_file, task):
        self.model_dir = model_dir
        self.data_file = data_file
        self.task = task
        self.prefix = os.path.splitext(os.path.basename(data_file))[0]

        with open(os.path.join(model_dir, 'config.yaml'), encoding='utf-8') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.target_cols = [i.strip() for i in config['Datahub']['target_cols'].split(',')]
            self.model_ids = [key for modelhub in config['Modelhub'].values() for key, item in modelhub.items() if item.get('active', False)]
            
        os.makedirs(os.path.join(model_dir, 'FrontEndData'), exist_ok=True)


    def get_metrics_json(self):
        json_file = os.path.join(self.model_dir, 'FrontEndData', 'model_metrics.json')
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
            return data

        csv_file = os.path.join(self.model_dir, 'EnsembleModel', 'model_metrics.csv')
        if not os.path.exists(csv_file):
            return {}
        df = pd.read_csv(csv_file)
        df['Models'] = df['Unnamed: 0'].apply(lambda x: x.split('_TAB_')[1] if '_TAB_' in x else x)
        df['Features'] = df['Unnamed: 0'].apply(lambda x: x.split('_TAB_')[2] if '_TAB_' in x else 'Meta_feature')
        df['Index'] = df['Unnamed: 0'].apply(lambda x: x.split('_TAB_')[0] if '_TAB_' in x else 'Ensemble')

        cols_list = ['Index', 'Models', 'Features', 
                     'auc', 'auprc', 'f1_score', 'mcc', 'acc', 'precision', 'recall', 'cohen_kappa', 
                     'r2', 'spearmanr', 'pearsonr', 'mse', 'mae',  'rmse', 'log_loss']
        df.drop(columns=['Unnamed: 0'], inplace=True)
        df = df.reindex(columns=cols_list)
        df.dropna(axis=1, how='all', inplace=True)
        df = df.sort_values('Index')
        df.to_json(json_file, orient='records')
        return df.to_dict(orient='records')

    def get_params_json(self):
        json_file = os.path.join(self.model_dir, 'FrontEndData', 'model_params.json')
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
            return data
        yaml_file = os.path.join(self.model_dir, 'config.yaml')
        if not os.path.exists(yaml_file):
            return {}
        with open(yaml_file, encoding='utf-8') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
        params_dict = {}
        for key in self.model_ids:
            if key.startswith('ML'):
                params_dict[key] = {}
                params_dict[key]['model'] = config['Modelhub']['MLModel'][key]['model']
                params_dict[key]['feature'] = config['Modelhub']['MLModel'][key]['feature']
                params_dict[key]['params'] = config['Modelhub']['MLModel'][key].get('params', None)
            elif key.startswith('NN'):
                params_dict[key] = {}
                params_dict[key]['model'] = config['Modelhub']['NNModel'][key]['model']
                params_dict[key]['feature'] = config['Modelhub']['NNModel'][key]['feature']
                if 'hyperopt' not in config['Modelhub']['NNModel'][key]:
                    params_dict[key]['params'] = {}
                    for k in ['max_epochs', 'learning_rate', 'batch_size']:
                        params_dict[key]['params'][k] = config['Trainer']['NNtrainer'][k]
                else:
                    params_dict[key]['params'] = config['Modelhub']['NNModel'][key]['hyperopt']
        params_dict['Ensemble'] = {}
        params_dict['Ensemble']['model']   = config['Ensembler']['model']
        params_dict['Ensemble']['feature'] = config['Ensembler']['feature']
        params_dict['Ensemble']['params']  = config['Ensembler'].get('params', {})
        for key in ['filter_size', 'method']:
            if key in config['Ensembler']:
                params_dict['Ensemble']['params'][key] = config['Ensembler'][key]
        with open(json_file, 'w') as f:
            json.dump(params_dict, f)
        return params_dict

    def get_model_details_by_key(self, key):
        json_file = os.path.join(self.model_dir, 'FrontEndData', key, 'model_details.json')
        #if os.path.exists(json_file):
        #    with open(json_file, 'r') as f:
        #        return json.load(f)

        details_file = os.path.join(self.model_dir, 'SummaryData', key, 'model_details.json')
        with open(details_file, 'r') as f:
            details = json.load(f)
        model_details = self.get_model_details_json(details)
        os.makedirs(os.path.dirname(json_file), exist_ok=True)
        with open(json_file, 'w') as f:
            json.dump(model_details, f)
        return model_details

    def get_ensemble_details(self):
        predict_dict = self.get_predict_json()
        ensemble_details = {}
        if self.task == 'classification':
            ensemble_details[self.target_cols[0]] = {}
            ensemble_details[self.target_cols[0]]['total'] = self.cal_roc_curve_data(predict_dict[self.target_cols[0]]['x'], predict_dict[self.target_cols[0]]['y'])
            temp_df = pd.DataFrame.from_dict(predict_dict[self.target_cols[0]])
            for fold in range(temp_df['fold'].nunique()):
                ensemble_details[self.target_cols[0]][fold] = self.cal_roc_curve_data(temp_df[temp_df['fold']==fold]['x'], temp_df[temp_df['fold']==fold]['y'])
        elif self.task == 'multilabel_classification':
            for i, target_col in enumerate(self.target_cols):
                ensemble_details[target_col] = {}
                ensemble_details[target_col]['total'] = self.cal_roc_curve_data(predict_dict[target_col]['x'], predict_dict[target_col]['y'])
                temp_df = pd.DataFrame.from_dict(predict_dict[target_col])
                for fold in range(temp_df['fold'].nunique()):
                    ensemble_details[target_col][fold] = self.cal_roc_curve_data(temp_df[temp_df['fold']==fold]['x'], temp_df[temp_df['fold']==fold]['y'])
        elif self.task == 'regression':
            ensemble_details[self.target_cols[0]] = {}
            ensemble_details[self.target_cols[0]]['total'] = {'true': predict_dict[self.target_cols[0]]['x'], 'pred': predict_dict[self.target_cols[0]]['y']}
            temp_df = pd.DataFrame.from_dict(predict_dict[self.target_cols[0]])
            for fold in range(temp_df['fold'].nunique()):
                ensemble_details[self.target_cols[0]][fold] = {'true': temp_df[temp_df['fold']==fold]['x'].tolist(), 'pred': temp_df[temp_df['fold']==fold]['y'].tolist()}
        elif self.task == 'multilabel_regression':
            for i, target_col in enumerate(self.target_cols):
                ensemble_details[target_col] = {}
                ensemble_details[target_col]['total'] = {'true': predict_dict[target_col]['x'], 'pred': predict_dict[target_col]['y']}
                temp_df = pd.DataFrame.from_dict(predict_dict[target_col])
                for fold in range(temp_df['fold'].nunique()):
                    ensemble_details[target_col][fold] = {'true': temp_df[temp_df['fold']==fold]['x'].tolist(), 'pred': temp_df[temp_df['fold']==fold]['y'].tolist()}
        elif self.task == 'multiclass':
            target_col = self.target_cols[0]
            ensemble_details[target_col] = {}
            ensemble_details[target_col]['total'] = self.cal_confusion_matrix(predict_dict[target_col]['x'], pred_value=predict_dict[target_col]['y'])
            #temp_df = pd.DataFrame.from_dict(predict_dict[target_col])
            #for fold in range(temp_df['fold'].nunique()):
            #    ensemble_details[target_col][fold] = self.cal_confusion_matrix(temp_df[temp_df['fold']==fold]['x'], pred_value=temp_df[temp_df['fold']==fold]['y'])
        return ensemble_details
        

    def get_all_details_json(self):
        json_file = os.path.join(self.model_dir, 'FrontEndData', 'all_details.json')
        #if os.path.exists(json_file):
        #    with open(json_file, 'r') as f:
        #        return json.load(f)
            
        all_details = {}
        for key in self.model_ids:
            all_details[key] = self.get_model_details_by_key(key)
        all_details['Ensemble'] = self.get_ensemble_details()
        with open(json_file, 'w') as f:
            json.dump(all_details, f)
        return all_details
    
    def cal_roc_curve_data(self, true_value, pred_value):
        fpr, tpr, _ = roc_curve(true_value, pred_value)
        return {'x': fpr.tolist(), 'y': tpr.tolist()}
    
    def cal_confusion_matrix(self, true_value, prob_value=None, pred_value=None):
        if prob_value is not None:
            pred_value = np.argmax(prob_value, axis=1)
        else:
            pred_value = np.array(pred_value)
        cm = confusion_matrix(true_value, pred_value)
        tp = np.diag(cm)
        fp = np.sum(cm, axis=0) - tp
        tn = np.sum(cm) - (fp + tp)
        fn = np.sum(cm, axis=1) - tp
        return {'tp': tp.tolist(), 'fp': fp.tolist(), 'fn': fn.tolist()}

    def get_model_details_json(self, details):
        model_details = {}
        if self.task == 'classification':
            model_details[self.target_cols[0]] = {}
            model_details[self.target_cols[0]]['total'] = self.cal_roc_curve_data(details['total']['true'], details['total']['pred']),
            for fold, data in details.items():
                if fold == 'total':
                    continue
                model_details[self.target_cols[0]][fold] = {
                    'train': self.cal_roc_curve_data(data['train']['true'], data['train']['pred']),
                    'test': self.cal_roc_curve_data(data['test']['true'], data['test']['pred'])
                }
        elif self.task == 'multilabel_classification':
            for i, target_col in enumerate(self.target_cols):
                model_details[target_col] = {}
                model_details[target_col]['total'] = self.cal_roc_curve_data(np.array(details['total']['true'])[:, i], np.array(details['total']['pred'])[:, i])
                for fold, data in details.items(): 
                    if fold == 'total':
                        continue                    
                    model_details[target_col][fold] = {
                        'train': self.cal_roc_curve_data(np.array(data['train']['true'])[:, i], np.array(data['train']['pred'])[:, i]),
                        'test': self.cal_roc_curve_data(np.array(data['test']['true'])[:, i], np.array(data['test']['pred'])[:, i])
                    }
        elif self.task == 'regression':
            for i, target_col in enumerate(self.target_cols):
                model_details[self.target_cols[0]] = {}
                model_details[self.target_cols[0]]['total'] = {'true': details['total']['true'], 'pred': details['total']['pred']}
                for fold, data in details.items():
                    if fold == 'total':
                        continue
                    model_details[self.target_cols[0]][fold] = {
                        'train': {'true': data['train']['true'], 'pred': data['train']['pred']},
                        'test': {'true': data['test']['true'], 'pred': data['test']['pred']}
                    }
        elif self.task == 'multilabel_regression':
            for i, target_col in enumerate(self.target_cols):
                model_details[target_col] = {}
                model_details[target_col]['total'] = {'true': np.array(details['total']['true'])[:, i].tolist(), 'pred': np.array(details['total']['pred'])[:, i].tolist()}
                for fold, data in details.items():
                    if fold == 'total':
                        continue
                    model_details[target_col][fold] = {
                        'train': {'true': np.array(data['train']['true'])[:, i].tolist(), 'pred': np.array(data['train']['pred'])[:, i].tolist()},
                        'test': {'true': np.array(data['test']['true'])[:, i].tolist(), 'pred': np.array(data['test']['pred'])[:, i].tolist()}
                    }
        elif self.task == 'multiclass':
            target_col = self.target_cols[0]
            model_details[target_col] = {}
            model_details[target_col]['total'] = self.cal_confusion_matrix(details['total']['true'], prob_value=details['total']['pred'])
            for fold, data in details.items():
                if fold == 'total':
                    continue
        return model_details

    def get_tsne_json(self):
        data_dir = os.path.join(self.model_dir, 'SummaryData')
        json_file = os.path.join(self.model_dir, 'FrontEndData', 'fp_tsne.json')
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                return json.load(f)
        
        tnse_file = os.path.join(data_dir, 'fp_tsne.txt')
        fold_file = os.path.join(data_dir, 'nfolds.txt')
        if not os.path.exists(tnse_file) or not os.path.exists(fold_file):
            return {}
        data = np.loadtxt(tnse_file, delimiter=',')
        fold = np.loadtxt(fold_file, delimiter=',')
        data = data.T.tolist()
        fold = fold.astype(int).tolist()
        json_data = {'x': data[0], 'y': data[1], 'fold': fold}
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        return json_data

    def get_predict_json(self):
        json_file = os.path.join(self.model_dir, 'FrontEndData', 'predict.json')
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                return json.load(f)
        csv_file = os.path.join(self.model_dir, 'EnsembleModel',  f'{self.prefix}.valid_0.csv')
        if not os.path.exists(csv_file):
            return {}
        df = pd.read_csv(csv_file)
        predict_dict = {}
        fold = np.loadtxt(os.path.join(self.model_dir, 'SummaryData', 'nfolds.txt'), delimiter=',').astype(int).tolist()
        if self.task in ['classification', 'multilabel_classification']:
            for target_col in self.target_cols:
                predict_dict[target_col] = {
                    'x': df[target_col].tolist(),
                    'y': df['prob_'+target_col].tolist(),
                    'fold': fold
                }
        elif self.task == 'multiclass':
            assert len(self.target_cols) == 1
            target_col = self.target_cols[0]
            predict_dict[target_col] = {
                'x': df[target_col].tolist(),
                'y': df['predict_'+target_col].tolist(),
                'fold': fold
            }
        elif self.task in ['regression', 'multilabel_regression']:
            for target_col in self.target_cols:
                predict_dict[target_col] = {
                    'x': df[target_col].tolist(),
                    'y': df['predict_'+target_col].tolist(),
                    'fold': fold
                }
        with open(json_file, 'w') as f:
            json.dump(predict_dict, f)
        return predict_dict

    def get_distribution_json(self):
        json_file = os.path.join(self.model_dir, 'FrontEndData', 'distribution.json')
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                return json.load(f)

        if self.data_file.endswith('.csv'):
            df = pd.read_csv(self.data_file)
        elif self.data_file.endswith('.sdf'):
            df = PandasTools.LoadSDF(self.data_file, removeHs=False) # type: ignore

        distribution_dict = {}
        for target_col in self.target_cols:
            df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
            if self.task in ['classification', 'multilabel_classification', 'multiclass']:
                counts = df[target_col].value_counts().sort_index().to_dict()
                result = {'x': list(counts.keys()), 'y': list(counts.values())}
            elif self.task in ['regression', 'multilabel_regression']:
                bins = pd.cut(df[target_col], bins=10)
                counts = bins.value_counts().sort_index().to_dict()
                result = {'x': [str(i) for i in list(counts.keys())], 'y': list(counts.values())}

            distribution_dict[target_col] = result

        with open(json_file, 'w') as f:
            json.dump(distribution_dict, f)
        return distribution_dict

    def get_all_json(self):
        metrics_json = self.get_metrics_json()
        distribution_json = self.get_distribution_json()
        tsne_json = self.get_tsne_json()
        predict_json = self.get_predict_json()
        params_json = self.get_params_json()
        model_details_json = self.get_all_details_json()
        return tsne_json, distribution_json , metrics_json, predict_json, params_json, model_details_json
    
if __name__ == '__main__':

    tasks = ['classification', 'regression', 'multilabel_classification', 'multilabel_regression', 'multiclass']
    for task in tasks:
        task = 'multiclass'
        data_file = f'/vepfs/fs_users/cuiyaning/uni-qsar/0821/optuna-dml/launch_test_files/datasets/train_{task}.csv'
        model_dir  = f'/vepfs/fs_users/cuiyaning/uni-qsar/0821/optuna-dml/launch_test_files/more_data2/{task}'
        converter = FrontEndData(model_dir, data_file, task)
        all_json = converter.get_all_json()
        break