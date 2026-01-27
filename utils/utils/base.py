from rdkit import Chem
from typing import Any, Literal, TypeGuard
import re
import pandas as pd
import matplotlib.pyplot as plt
import squarify
import seaborn as sns


def is_str(val: Any) -> TypeGuard[str]:
    return isinstance(val, str)

def is_sql_val(val: Any) -> bool:
    return is_str(val) and not bool(re.search(r'\s', val))

def is_str_list(val: Any) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def is_number_or_None(val: Any) -> TypeGuard[float|int|None]:
    return isinstance(val, (float, int, type(None)))
    

def is_smiles_or_smarts(s:str) -> Literal['smiles','smarts',False]:
    try:
        mol1 = Chem.MolFromSmiles(s) # type: ignore
        mol2 = Chem.MolFromSmarts(s) # type: ignore
        if mol1 and not mol2:
            return "smiles"
        elif mol2 and not mol1:
            return "smarts"
        else:
            # 两者都能解析，进一步判定
            if any(x in s for x in ['&', ',', ';', '!', '[#', '[a', '[A']):
                return "smarts"
            else:
                return "smiles"
    except Exception as e:
        return False
    
def is_valid_smiles(s:str) -> bool:
    try:
        mol = Chem.MolFromSmiles(s) # type: ignore
        return mol is not None
    except Exception as e:
        return False
    

def count_EZ_in_smiles(smiles_list):
    potential_EZ_count = 0
    explicit_EZ_count = 0

    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue

        Chem.AssignStereochemistry(mol, force=True, cleanIt=True)

        has_potential = False
        has_explicit = False

        for bond in mol.GetBonds():
            if bond.GetBondType() != Chem.rdchem.BondType.DOUBLE:
                continue

            a1, a2 = bond.GetBeginAtom(), bond.GetEndAtom()
            # 判断是否具有潜在E/Z构型
            n1 = [nbr.GetIdx() for nbr in a1.GetNeighbors() if nbr.GetIdx() != a2.GetIdx()]
            n2 = [nbr.GetIdx() for nbr in a2.GetNeighbors() if nbr.GetIdx() != a1.GetIdx()]
            if len(set(n1)) >= 1 and len(set(n2)) >= 1:
                has_potential = True

            # 判断是否明确标记E/Z
            stereo = bond.GetStereo()
            if stereo in (Chem.rdchem.BondStereo.STEREOE, Chem.rdchem.BondStereo.STEREOZ):
                has_explicit = True

        if has_potential:
            potential_EZ_count += 1
        if has_explicit:
            explicit_EZ_count += 1

    return potential_EZ_count, explicit_EZ_count

def batch_count_EZ_in_smiles(smiles_list, batch_size=1000):
    count_with_chiral_centers = 0   # 包括未指定的
    count_with_defined_chirality = 0  # 明确 R/S

    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        
        # 检查是否有手性中心（包括未指定的）
        centers_all = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
        if len(centers_all) > 0:
            count_with_chiral_centers += 1

        # 检查是否有明确手性中心（只算指定了 R/S）
        centers_defined = Chem.FindMolChiralCenters(mol, includeUnassigned=False)
        if len(centers_defined) > 0:
            count_with_defined_chirality += 1

    return count_with_chiral_centers, count_with_defined_chirality


def draw_label_distribution_bar(
    odor_counts: dict[str, int],
    top_n: int = 50,
    output_path: str = "odor_distribution_bar.svg"
) -> None:
    """
    Draw a bar chart for top-N odor label frequencies.
    """

    # dict → Series → 排序
    series = (
        pd.Series(odor_counts, name="count")
        .sort_values(ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(top_n * 0.25, 6))

    series.plot(kind="bar", ax=ax)

    ax.set_xlabel("Odor Labels")
    ax.set_ylabel("Number of Molecules")
    ax.set_title(f"Top {top_n} Odor Labels Distribution")
    ax.tick_params(axis="x", rotation=45)

    # 数值标注
    ax.bar_label(
        ax.containers[0], # type: ignore
        label_type="edge",
        fontsize=8,
        rotation=90,
        padding=2
    )

    plt.tight_layout()
    plt.savefig(output_path, format="svg")
    plt.show()


def draw_label_distribution_treemap(
    odor_counts: dict[str, int],
    quantile_threshold: float = 0.8,
    output_path: str = "odor_distribution_treemap.svg"
) -> None:
    """
    Draw a treemap visualization for odor label distribution.
    Only labels above the given quantile threshold will be annotated.
    """

    # dict → DataFrame（标准 schema）
    df = (
        pd.Series(odor_counts, name="count")
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"index": "odor_label"})
    )

    # 调色板
    palette = sns.color_palette("Set3", len(df))
    colors = palette[: len(df)]

    # 标签显示阈值
    threshold = df["count"].quantile(quantile_threshold)

    labels = [
        f"{label}\n{count}" if count >= threshold else ""
        for label, count in zip(df["odor_label"], df["count"])
    ]

    plt.figure(figsize=(16, 10))
    squarify.plot(
        sizes=df["count"],
        label=labels,
        color=colors,
        alpha=0.85,
        text_kwargs={"fontsize": 9}
    )

    plt.title("Odor Label Distribution (Treemap)", fontsize=18, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, format="svg")
    plt.show()


