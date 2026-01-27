from typing import TypeVar, Generic, cast
from pydantic import BaseModel
import json
import pandas as pd
import numpy as np
from rdkit.Chem import PandasTools
import yaml
import asyncio
from sklearn.metrics import roc_curve, confusion_matrix
from pathlib import Path
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorCollection
from ...db.utils import DB,AsyncIOMotorDatabase
from ...task.task_manager import DB_Operation as OP
import logging
from fastapi import HTTPException, status

qsarDB: AsyncIOMotorDatabase = cast(AsyncIOMotorDatabase, DB.db)
user_collection: AsyncIOMotorCollection  = qsarDB['user']
task_collection: AsyncIOMotorCollection  = qsarDB['task']

logger = logging.getLogger("app")

# raw_files, vaild_files
EXPERIMENT_Fit = "my_experiment_fit"
EXPERIMENT_Infer = "my_experiment_infer"
MODELS_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/models"
MLRESULTS_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/mlruns"
FILES_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/files"
# mlflow experiment id
MLFLOW_EXPERIMENT_FIT='783693552791073446'
MLFLOW_EXPERIMENT_OLD_FIT='546302617315522606'
MLFLOW_EXPERIMENT_INFER='639031919007598614'
# f"{MODELS_DIR}/{experiment.experiment_id}/{run_id}

T = TypeVar("T")

class RES(BaseModel, Generic[T]):
    code: int = 0
    data: T | None = None
    msg: str = ""

@dataclass
class ChartData:
    run_id: str
    data_path: Path = field(init=False)
    model_dir: Path = field(init=False)
    model_run_ids: list[str] = field(init=False)
    config_path: Path = field(init=False)
    config_dict: dict = field(init=False)
    target_cols: list[str] = field(init=False)
    cache4req_dir: Path = field(init=False)

    async def async_init(self):
        task = await OP.get_task_info(self.run_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"model run_id: {self.run_id} not found",
            )
        else:
            self.data_path = task.data_path
        self.model_dir = Path(MODELS_DIR, MLFLOW_EXPERIMENT_FIT, self.run_id)
        self.config_path = Path(self.model_dir, "config.yaml")
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config_dict = yaml.safe_load(f)
                    self.target_cols = [
                        col.strip()
                        for col in self.config_dict["Datahub"]["target_cols"].split(",")
                    ]
                    self.model_run_ids = [
                        key
                        for modelhub in self.config_dict["Modelhub"].values()
                        	for key, item in modelhub.items()
                        		if item.get("active", False)
                    ]
            except Exception as e:
                logger.error(f"读取YAML文件时发生错误: {e}")
        else:
            raise ValueError(f"no config.yaml file, run_id:{self.run_id}")
        self.cache4req_dir = Path(self.model_dir, "cache4req")
        if not self.cache4req_dir.exists():
            self.cache4req_dir.mkdir()

    def get_metrics_json(self):
        json_file = Path(self.cache4req_dir, "model_metrics.json")
        if json_file.exists():
            with open(json_file, "r") as f:
                data = json.load(f)
            return data

        csv_file = Path(self.model_dir, "EnsembleModel", "model_metrics.csv")
        if not csv_file.exists():
            return {}
        df = pd.read_csv(csv_file)
        df["Models"] = df["Unnamed: 0"].apply(
            lambda x: x.split("_TAB_")[1] if "_TAB_" in x else x
        )
        df["Features"] = df["Unnamed: 0"].apply(
            lambda x: x.split("_TAB_")[2] if "_TAB_" in x else "Meta_feature"
        )
        df["Index"] = df["Unnamed: 0"].apply(
            lambda x: x.split("_TAB_")[0] if "_TAB_" in x else "Ensemble"
        )

        cols_dict: dict[str, str] = {
            "Index": "Index",
            "Models": "Models",
            "Features": "Features",
            "auc": "AUC",
            "auprc": "AUPRC",
            "f1_score": "F1_score",
            "mcc": "MCC",
            "acc": "ACC",
            "precision": "Precision",
            "recall": "Recall",
            "cohen_kappa": "Cohen_kappa",
            "r2": "R2",
            "spearmanr": "Spearmanr",
            "pearsonr": "Pearsonr",
            "mse": "MSE",
            "mae": "MAE",
            "rmse": "RMSE",
            "log_loss": "Log_loss"
        }
        df.drop(columns=["Unnamed: 0"], inplace=True)
        df = df.reindex(columns=list(cols_dict.keys()))
        df.rename(columns=cols_dict, inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        df = df.sort_values("Index")
        df.to_json(json_file, orient="records")
        return df.to_dict(orient="records")

    def get_params_json(self):
        json_file = Path(self.cache4req_dir, "model_params.json")
        if json_file.exists():
            with open(json_file, "r") as f:
                data = json.load(f)
            return data

        params_dict = {}
        for key in self.model_run_ids:
            if key.startswith("ML"):
                params_dict[key] = self.config_dict["Modelhub"]["MLModel"][key]
            elif key.startswith("NN"):
                params_dict[key] = self.config_dict["Modelhub"]["NNModel"][key]
                if "hyperopt" not in params_dict[key]:
                    params_dict[key]["hyperopt"] = {}
                    for k in ["max_epochs", "learning_rate", "batch_size"]:
                        params_dict[key]["hyperopt"][k] = self.config_dict["Trainer"][
                            "NNtrainer"
                        ][k]
        params_dict["Ensemble"] = self.config_dict["Ensembler"]
        with open(json_file, "w") as f:
            json.dump(params_dict, f)
        return params_dict

    def cal_roc_curve_data(self, true_value, pred_value):
        fpr, tpr, _ = roc_curve(true_value, pred_value)
        return {"x": fpr.tolist(), "y": tpr.tolist()}
    
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

        def round_nested_dict(d):
            for key, value in d.items():
                if isinstance(value, dict):
                    round_nested_dict(value)
                elif isinstance(value, list):
                    d[key] = np.round(np.array(value), 4).tolist()
            return d

        if self.config_dict["Base"]["task"] == "classification":
            model_details[self.target_cols[0]] = {}
            model_details[self.target_cols[0]]["total"] = (
                self.cal_roc_curve_data(
                    details["total"]["true"], details["total"]["pred"]
                ),
            )
            for fold, data in details.items():
                if fold == "total":
                    continue
                model_details[self.target_cols[0]][fold] = {
                    "train": self.cal_roc_curve_data(
                        data["train"]["true"], data["train"]["pred"]
                    ),
                    "test": self.cal_roc_curve_data(
                        data["test"]["true"], data["test"]["pred"]
                    ),
                }
        elif self.config_dict["Base"]["task"] == "multilabel_classification":
            for i, target_col in enumerate(self.target_cols):
                model_details[target_col] = {}
                model_details[target_col]["total"] = self.cal_roc_curve_data(
                    np.array(details["total"]["true"])[:, i],
                    np.array(details["total"]["pred"])[:, i],
                )
                for fold, data in details.items():
                    if fold == "total":
                        continue
                    model_details[target_col][fold] = {
                        "train": self.cal_roc_curve_data(
                            np.array(data["train"]["true"])[:, i],
                            np.array(data["train"]["pred"])[:, i],
                        ),
                        "test": self.cal_roc_curve_data(
                            np.array(data["test"]["true"])[:, i],
                            np.array(data["test"]["pred"])[:, i],
                        ),
                    }
        elif self.config_dict["Base"]["task"] == "regression":
            for i, target_col in enumerate(self.target_cols):
                model_details[self.target_cols[0]] = {}
                model_details[self.target_cols[0]]["total"] = {
                    "true": details["total"]["true"],
                    "pred": details["total"]["pred"],
                }
                for fold, data in details.items():
                    if fold == "total":
                        continue
                    model_details[self.target_cols[0]][fold] = {
                        "train": {
                            "true": data["train"]["true"],
                            "pred": data["train"]["pred"],
                        },
                        "test": {
                            "true": data["test"]["true"],
                            "pred": data["test"]["pred"],
                        },
                    }
            model_details = round_nested_dict(model_details)
        elif self.config_dict["Base"]["task"] == "multilabel_regression":
            for i, target_col in enumerate(self.target_cols):
                model_details[target_col] = {}
                model_details[target_col]["total"] = {
                    "true": np.array(details["total"]["true"])[:, i].tolist(),
                    "pred": np.array(details["total"]["pred"])[:, i].tolist(),
                }
                for fold, data in details.items():
                    if fold == "total":
                        continue
                    model_details[target_col][fold] = {
                        "train": {
                            "true": np.array(data["train"]["true"])[:, i].tolist(),
                            "pred": np.array(data["train"]["pred"])[:, i].tolist(),
                        },
                        "test": {
                            "true": np.array(data["test"]["true"])[:, i].tolist(),
                            "pred": np.array(data["test"]["pred"])[:, i].tolist(),
                        },
                    }
            model_details = round_nested_dict(model_details)
        elif self.config_dict["Base"]["task"] == 'multiclass':
            target_col = self.target_cols[0]
            model_details[target_col] = {}
            model_details[target_col]['total'] = self.cal_confusion_matrix(details['total']['true'], prob_value=details['total']['pred'])
            for fold, data in details.items():
                if fold == 'total':
                    continue
        return model_details

    def get_model_details_by_key(self, key):
        json_file = Path(self.cache4req_dir, key, "model_details.json")
        if json_file.exists():
            with open(json_file, "r") as f:
                return json.load(f)

        details_file = Path(self.model_dir, "SummaryData", key, "model_details.json")
        if details_file.exists():
            with open(details_file, "r") as f:
                details = json.load(f)
            model_details = self.get_model_details_json(details)
        else:
            return {}
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, "w") as f:
            json.dump(model_details, f)
        return model_details

    def get_ensemble_details(self):
        predict_dict = self.get_predict_json()
        ensemble_details = {}
        if self.config_dict["Base"]["task"] == 'classification':
            ensemble_details[self.target_cols[0]] = {}
            ensemble_details[self.target_cols[0]]['total'] = self.cal_roc_curve_data(predict_dict[self.target_cols[0]]['x'], predict_dict[self.target_cols[0]]['y'])
            temp_df = pd.DataFrame.from_dict(predict_dict[self.target_cols[0]])
            for fold in range(temp_df['fold'].nunique()):
                ensemble_details[self.target_cols[0]][fold] = self.cal_roc_curve_data(temp_df[temp_df['fold']==fold]['x'], temp_df[temp_df['fold']==fold]['y'])
        elif self.config_dict["Base"]["task"] == 'multilabel_classification':
            for i, target_col in enumerate(self.target_cols):
                ensemble_details[target_col] = {}
                ensemble_details[target_col]['total'] = self.cal_roc_curve_data(predict_dict[target_col]['x'], predict_dict[target_col]['y'])
                temp_df = pd.DataFrame.from_dict(predict_dict[target_col])
                for fold in range(temp_df['fold'].nunique()):
                    ensemble_details[target_col][fold] = self.cal_roc_curve_data(temp_df[temp_df['fold']==fold]['x'], temp_df[temp_df['fold']==fold]['y'])
        elif self.config_dict["Base"]["task"] == 'regression':
            ensemble_details[self.target_cols[0]] = {}
            ensemble_details[self.target_cols[0]]['total'] = {'true': predict_dict[self.target_cols[0]]['x'], 'pred': predict_dict[self.target_cols[0]]['y']}
            temp_df = pd.DataFrame.from_dict(predict_dict[self.target_cols[0]])
            for fold in range(temp_df['fold'].nunique()):
                ensemble_details[self.target_cols[0]][fold] = {'true': temp_df[temp_df['fold']==fold]['x'].tolist(), 'pred': temp_df[temp_df['fold']==fold]['y'].tolist()}
        elif self.config_dict["Base"]["task"] == 'multilabel_regression':
            for i, target_col in enumerate(self.target_cols):
                ensemble_details[target_col] = {}
                ensemble_details[target_col]['total'] = {'true': predict_dict[target_col]['x'], 'pred': predict_dict[target_col]['y']}
                temp_df = pd.DataFrame.from_dict(predict_dict[target_col])
                for fold in range(temp_df['fold'].nunique()):
                    ensemble_details[target_col][fold] = {'true': temp_df[temp_df['fold']==fold]['x'].tolist(), 'pred': temp_df[temp_df['fold']==fold]['y'].tolist()}
        elif self.config_dict["Base"]["task"] == 'multiclass':
            target_col = self.target_cols[0]
            ensemble_details[target_col] = {}
            ensemble_details[target_col]['total'] = self.cal_confusion_matrix(predict_dict[target_col]['x'], pred_value=predict_dict[target_col]['y'])
        return ensemble_details
    
    def get_all_details_json(self):
        json_file = Path(self.cache4req_dir, 'all_details.json')
        if json_file.exists():
            with open(json_file, 'r') as f:
                return json.load(f)
            
        all_details = {}
        for key in self.model_run_ids:
            all_details[key] = self.get_model_details_by_key(key)
        all_details['Ensemble'] = self.get_ensemble_details()
        with open(json_file, 'w') as f:
            json.dump(all_details, f)
        return all_details

    def get_tsne_json(self):
        data_dir = Path(self.model_dir, "SummaryData")
        json_file = Path(self.cache4req_dir, "fp_tsne.json")
        if json_file.exists():
            with open(json_file, "r") as f:
                return json.load(f)

        tnse_file = Path(data_dir, "fp_tsne.txt")
        fold_file = Path(data_dir, "nfolds.txt")
        if not tnse_file.exists() or not fold_file.exists():
            return {}
        data = np.loadtxt(tnse_file, delimiter=",")
        fold = np.loadtxt(fold_file, delimiter=",")
        data = data.T.tolist()
        fold = fold.astype(int).tolist()
        json_data = {"x": data[0], "y": data[1], "fold": fold}
        with open(json_file, "w") as f:
            json.dump(json_data, f)
        return json_data

    def get_predict_json(self):
        json_file = Path(self.cache4req_dir, "predict.json")
        if json_file.exists():
            with open(json_file, "r") as f:
                return json.load(f)
        csv_file = Path(
            self.model_dir, "EnsembleModel", f"{self.data_path.stem}.valid_0.csv"
        )
        if not csv_file.exists():
            return {}
        df = pd.read_csv(csv_file)
        predict_dict = {}
        fold = (
            np.loadtxt(Path(self.model_dir, "SummaryData", "nfolds.txt"), delimiter=",")
            .astype(int)
            .tolist()
        )
        if self.config_dict["Base"]["task"] in [
            "classification",
            "multilabel_classification",
        ]:
            for target_col in self.target_cols:
                predict_dict[target_col] = {
                    "x": df[target_col].tolist(),
                    "y": df["prob_" + target_col].tolist(),
                    "fold": fold,
                }
        elif self.config_dict["Base"]["task"] == "multiclass":
            target_col = self.target_cols[0]
            predict_dict[target_col] = {
                "x": df[target_col].tolist(),
                "y": df["predict_" + target_col].tolist(),
                "fold": fold,
            }
        elif self.config_dict["Base"]["task"] in [
            "regression",
            "multilabel_regression",
        ]:
            for target_col in self.target_cols:
                predict_dict[target_col] = {
                    "x": df[target_col].tolist(),
                    "y": df["predict_" + target_col].tolist(),
                    "fold": fold,
                }
        with open(json_file, "w") as f:
            json.dump(predict_dict, f)
        return predict_dict

    def get_distribution_json(self):
        json_file = Path(self.cache4req_dir, "distribution.json")
        if json_file.exists():
            with open(json_file, "r") as f:
                return json.load(f)

        if self.data_path.suffix == ".csv":
            df = pd.read_csv(self.data_path)
        elif self.data_path.suffix == ".sdf":
            df = PandasTools.LoadSDF(self.data_path, removeHs=False)  # type: ignore

        distribution_dict = {}
        for target_col in self.target_cols:
            df[target_col] = df[target_col].astype(float)
            distribution_dict[target_col] = df[target_col].tolist()

        with open(json_file, "w") as f:
            json.dump(distribution_dict, f)
        return distribution_dict

    def get_all_json(self):
        out = {
            "metrics": self.get_metrics_json(),
            "distribution": self.get_distribution_json(),
            "tsne_json": self.get_tsne_json(),
            "predict": self.get_predict_json(),
            "params": self.get_params_json(),
            "all_model_details": self.get_all_details_json(),
        }
        return out
