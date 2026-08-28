# Garde en memoire toutes les donnees chargees et gere leur filtrage/tri

import pandas as pd
from infrastructure.extractors.excel_extractor import extract_all_sheets
from infrastructure.models.pandas_model import PandasModel

class DataService:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = DataService()
        return cls._instance

    def __init__(self):
        self.df_all: pd.DataFrame = pd.DataFrame()
        self.summaries: dict = {}
        self.loaded_uids: set[str] = set()

    @property
    def df_all(self): return self.df_all
    @property
    def summaries(self): return self.summaries
    @property
    def loaded_uids(self): return self.loaded_uids

    def load_files(self, filepaths: list[str]) -> set[str]:
        new_df, new_sum, new_uids = extract_all_sheets(filepaths, self.loaded_uids)
        if not new_uids:
            return set()
        self.loaded_uids |= new_uids
        self.summaries.update(new_sum)
        self.df_all = new_df if self.df_all.empty else pd.concat([self.df_all, new_df], ignore_index=True)
        return new_uids

    def remove_file(self, source_uid: str) -> None:
        self.loaded_uids.discard(source_uid)
        self.df_all = self.df_all[self.df_all["source_uid"] != source_uid].reset_index(drop=True)
        self.summaries.pop(source_uid, None)

    def filtered_df(self, filter_sidebar=None, sort_col: str = None, asc: bool = True):
        if self.df_all.empty:
            return pd.DataFrame(columns=PandasModel.COLS)
        df = self.df_all.copy()
        if filter_sidebar is not None:
            try:
                df = filter_sidebar.apply(df)
            except Exception:
                pass
        if sort_col and sort_col in df.columns:
            try:
                df = df.sort_values(sort_col, ascending=asc).reset_index(drop=True)
            except Exception:
                pass
        return df

    def reset(self) -> None:
        self.df_all = pd.DataFrame()
        self.summaries.clear()
        self.loaded_uids.clear()
