from pydantic import BaseModel, model_validator, Field
from typing import Union, TypeVar, Generic, Literal, Any, TypeGuard
from loguru import logger
from src.utils.base import (
    is_str,
    is_str_list,
    is_smiles_or_smarts,
    is_valid_smiles,
    is_number_or_None,
    is_sql_val,
)

T = TypeVar("T")


class RES(BaseModel, Generic[T]):
    code: int = 0
    data: Union[T, None] = None
    msg: str = ""

    @model_validator(mode="after")
    def log_msg(self):
        if self.msg:
            msg_down = self.msg.upper()
            if msg_down.startswith("info"):
                message = self.msg[len("info") :].lstrip(":").lstrip()
                logger.info(message)
            elif msg_down.startswith("error"):
                message = self.msg[len("error") :].lstrip(":").lstrip()
                logger.error(message)
            else:
                # Default logging level
                logger.info(self.msg)
        return self


class Conf(BaseModel):
    name: str = ""
    molblock: str = ""
    energy: float = 0.0

class DataId(BaseModel):
    id: int

class Count(BaseModel):
    count: int

F = TypeVar("F")
class PageInfo(BaseModel,Generic[F]):
    offset: int = 0
    limit: int = 100
    filters: list[F] = []


class MolBase(BaseModel):
    id: int = 0  # 数据库中的id一定会 > 0
    smiles: str

    def dump_without_id(self):
        out = self.model_dump()
        del out["id"]
        return out


class MolDB(MolBase):
    mfp: str | None = None
    tfp: str | None = None
    inchi: str | None = None
    inchi_key: str | None = None
    cas: str | None = None
    formula: str | None = None
    mol_aweight: float | None = None
    mol_eweight: float | None = None
    odor_labels: list[str] | None = None
    odor_threshold: float | None = None
    description: str | None = None
    source: str | None = None
    ctime: float | None = None
    conformers: list[Conf] | None = None
    info: dict | None = None


class SearchRES(BaseModel):
    items: list[MolBase]
    total: int


class QueryOptions(BaseModel):
    adjustDegree: bool = Field(
        default=True, description="adds a query to match the input atomic degree"
    )
    adjustDegreeFlags: str | None = Field(
        default="ADJUST_IGNOREDUMMIES | ADJUST_IGNORECHAINS",
        description="controls where the degree is adjusted",
    )
    adjustRingCount: bool = Field(
        default=False, description="adds a query to match the input ring count"
    )
    adjustRingCountFlags: str | None = Field(
        default="ADJUST_IGNOREDUMMIES | ADJUST_IGNORECHAINS",
        description="controls where the ring count is adjusted",
    )
    makeDummiesQueries: bool = Field(
        default=True,
        description="convert dummy atoms in the input structure into any-atom queries",
    )
    aromatizeIfPossible: bool = Field(
        default=True,
        description="run the aromaticity perception algorithm on the input structure ",
    )
    makeBondsGeneric: bool = Field(
        default=False, description="convert bonds into any-bond queries"
    )
    makeBondsGenericFlags: bool = Field(
        default=False, description="controls which bonds are made generic"
    )
    makeAtomsGeneric: bool = Field(
        default=False, description="convert atoms into any-atom queries"
    )
    makeAtomsGenericFlags: bool = Field(
        default=False, description="controls which atoms are made generic"
    )
    setGenericQueryFromProperties: bool = Field(
        default=False, description="controls if generic groups can be queried"
    )


class ItemSQL(BaseModel):
    sql: str
    setting: list[str]


class FilterItem(BaseModel):
    logic: Literal["and", "or", "not"]
    field: Literal[
        "substructure",
        "similarity",
        "inchi",
        "inchi_key",
        "cas",
        "formula",
        "mol_aweight",
        "mol_eweight",
        "ctime",
        "odor_threshold",
        "odor_labels",
    ]
    operator: Literal["@=", "@>", "<@", "&&"] | None = None
    value: tuple[
        str | list[str] | None, 
        float | None, 
        float | None
    ]
    settings: list[str] = []

    def to_sql_str(self) -> ItemSQL:
        selfStr: str = ""
        down: float | None = self.value[1]
        up: float | None = self.value[2]
        if not is_number_or_None(down) or not is_number_or_None(up):
            raise ValueError(f"Invalid value type : {self.value}")

        if self.field == "substructure":
            if not isinstance(self.value[0], str):
                raise ValueError(f"Invalid value type: {self.value[0]}")

            operator = self.operator
            if operator not in ["@=", "@>", "<@"]:
                raise ValueError(f"Invalid operator: {operator}")

            # self.settings like ['do_chiral_sss','do_enhanced_stereo_sss']
            tmp = []
            for setting in set(self.settings):
                if setting in ["do_chiral_sss", "do_enhanced_stereo_sss"]:
                    tmp.append(f"SET rdkit.{setting}=true;")
            self.settings = tmp

            smi = self.value[0]
            type = is_smiles_or_smarts(smi)
            if type == "smiles":
                selfStr = f"(mol{operator}'{smi}')"
            elif type == "smarts":
                selfStr = f"(mol{operator}mol_adjust_query_properties('{smi}'))"
            else:
                raise ValueError(f"Invalid SMILES or SMARTS: {self.value[1]}")

        elif self.field == "similarity":
            if not isinstance(self.value[0], str):
                raise ValueError(f"Invalid value type : {self.value}")
            smi = self.value[0]
            if not is_valid_smiles(smi):
                raise ValueError(f"Invalid SMILES: {smi}")

            self.settings = []
            self.settings.append(
                f"SET rdkit.tanimoto_threshold={down if (down is not None) else 0.5};"
            )
            if up == 100 or up is None:
                selfStr = f"(morganbv_fp(mol_from_smiles('{smi}')) % mfp)"
            else:
                selfStr = f"(morganbv_fp(mol_from_smiles('{smi}')) % mfp AND tanimoto_sml(morganbv_fp(mol_from_smiles('{smi}')), mfp) <= {up/100})"

        elif self.field == "inchi":
            if not is_sql_val(self.value[0]):
                raise ValueError(f"Invalid value type : {self.value}")
            inchi = self.value[0]
            self.settings = []
            self.settings.append(
                f"SET pg_trgm.similarity_threshold={down if (down is not None) else 0.5};"
            )
            if up == 1.0 or up is None:
                selfStr = f"(inchi % '{inchi}')"
            else:
                selfStr = (
                    f"(inchi % '{inchi}' AND similarity(inchi, '{inchi}') <= {up})"
                )

        elif self.field == "inchi_key":
            if not is_sql_val(self.value[0]):
                raise ValueError(f"Invalid value type : {self.value}")
            inchi_key = self.value[0]
            selfStr = f"(inchi_key = '{inchi_key}')"

        elif self.field == "cas":
            if not is_sql_val(self.value[0]):
                raise ValueError(f"Invalid value type : {self.value}")
            cas = self.value[0]
            selfStr = f"(cas = '{cas}')"

        elif self.field == "formula":
            if not is_sql_val(self.value[0]):
                raise ValueError(f"Invalid value type : {self.value}")
            formula = self.value[0]
            selfStr = f"(formula = '{formula}')"

        elif self.field == "mol_aweight":
            if (down is None) and (up is None):
                raise ValueError("Invalid value for aweight")
            elif (down is not None) and (up is not None):
                selfStr = f"(mol_aweight BETWEEN {down} AND {up})"
            elif up is not None:
                selfStr = f"(mol_aweight<={up})"
            else:  # down is not None
                selfStr = f"(mol_aweight>={down})"

        elif self.field == "mol_eweight":
            if (down is None) and (up is None):
                raise ValueError("Invalid value for eweight")
            elif (down is not None) and (up is not None):
                selfStr = f"(mol_eweight BETWEEN {down} AND {up})"
            elif up is not None:
                selfStr = f"(mol_eweight<={up})"
            else:  # down is not None
                selfStr = f"(mol_eweight>={down})"

        elif self.field == "ctime":
            if (down is None) and (up is None):
                raise ValueError("Invalid value for ctime")
            elif (down is not None) and (up is not None):
                selfStr = f"(ctime BETWEEN {down} AND {up})"
            elif up is not None:
                selfStr = f"(ctime<={up})"
            else:  # down is not None
                selfStr = f"(ctime>={down})"

        elif self.field == "odor_threshold":
            if (down is None) and (up is None):
                raise ValueError("Invalid value for odor_threshold")
            elif (down is not None) and (up is not None):
                selfStr = f"(odor_threshold BETWEEN {down} AND {up})"
            elif up is not None:
                selfStr = f"(odor_threshold<={up})"
            else:  # down is not None
                selfStr = f"(odor_threshold>={down})"

        elif self.field == "odor_labels":
            if not is_str_list(self.value[0]):
                raise ValueError(f"odor_labels error in is_str_list(): {self.value}")
            list_item_str = "','".join(self.value[0])
            operator = self.operator
            if operator not in ["@>", "&&"]:
                raise ValueError(f"Invalid operator: {operator}, expect '@>' or '&&'")
            selfStr = f"(odor_labels {operator} ARRAY['{list_item_str}'])"

        else:
            raise ValueError(f"Invalid field: {self.field}")

        return ItemSQL(sql=selfStr, setting=self.settings)
