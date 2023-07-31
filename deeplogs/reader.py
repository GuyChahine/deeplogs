from os import listdir, PathLike
import pandas as pd
import matplotlib.pyplot as plt
from math import ceil
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import Literal, Callable

from deeplogs.logger import Log

class Reader():
    
    """
    A utility to read and analyze logs generated during the training or execution of multiple models.

    Args:
        log_names (list of str, optional): List of session names to load. Default is all sessions.
        log_folder_path (PathLike or str, optional): Path to the folder where logs are saved. Default is './dplogs/'.
    """
    
    def __init__(
        self,
        log_names: list[str] = [],
        log_folder_path: PathLike|str = "./dplogs/",
    ):
        self.PLOT_USING: dict[str: Callable] = {
            "plotly": self.__scalar_plotly,
            "matplotlib": self.__scalar_plt,
        }
        
        self.log_folder_path: str = log_folder_path
        self.log_names: list[str] = log_names if len(log_names) > 0 else listdir(log_folder_path)
        
        self.LS: list[Log] = [Log.load(self.log_folder_path + log_name + "/.log") for log_name in self.log_names]
    
    def describe(self, name: list[str] = [], percentiles: list[float] = [0.25, 0.5, 0.75, 0.9]) -> pd.DataFrame:
        
        """
        Generate descriptive statistics of the scalar logs.

        Args:
            name (list of str, optional): List of session names for which statistics will be generated. Default is all.
            percentiles (list of float, optional): List of percentiles to include in the statistics. Default is [0.25, 0.5, 0.75, 0.9].

        Returns:
            pd.DataFrame: A DataFrame containing descriptive statistics.
        """
        
        if not name: name = [L.name for L in self.LS]
        describe_dfs: list[pd.DataFrame] = []
        for L in self.LS:
            if L.name not in name: continue
            df = L.scalar_to_dataframe().describe(percentiles=percentiles)
            df.index = pd.MultiIndex.from_product([[L.name], df.index])
            describe_dfs.append(df)
        return pd.concat(describe_dfs)
    
    def infos(self, name: list[str] = []) -> pd.DataFrame:
        
        """
        Generate a summary of sessions information.

        Args:
            name (list of str, optional): List of session names for which information will be generated. Default is all.

        Returns:
            pd.DataFrame: A DataFrame containing the informations.
        """
        
        if not name: name = [L.name for L in self.LS]
        return pd.concat([pd.Series(
            {"name": L.name, "description": L.description, **L.hyperparams}    
        ).to_frame().T for L in self.LS if L.name in name]).set_index("name", drop=True)
            
    FIGSIZE_TRANSLATION: dict[str: float] = {
        "matplotlib": 1.,
        "plotly": 75.,
    }
    
    def scalar(
        self,
        logs: list[str] = [],
        using: Literal["plotly", "matplotlib"] = "plotly",
        ncols: int = 2,
        figsize: tuple[int, int] = (20,10),
        xlabel: str = "timestep",
        smooth_perc: float = 0.99,
    ) -> None:
        
        """
        Plot scalar logs over timesteps using different visualization libraries.

        Args:
            logs (list of str, optional): List of scalar log names to plot. Default is all.
            using (Literal["plotly", "matplotlib"], optional): Visualization library to use for plotting. Default is "plotly".
            ncols (int, optional): Number of columns in the plot grid. Default is 2.
            figsize (tuple of int, optional): Figure size (width, height) for the plot. Default is (20, 10).
            xlabel (str, optional): Label for the x-axis in the plot. Default is "timestep".
            smooth_perc (float, optional): Percentage of smoothing for the plot. Default is 0.99.
        """
        
        figsize = tuple(map(lambda x: int(x*self.FIGSIZE_TRANSLATION[using]), figsize))
        dfs = pd.concat([L.scalar_to_dataframe() for L in self.LS], axis=0)
        if not logs: logs = dfs.columns.to_list()
        nrows: int = int(ceil(len(logs) / ncols))
        
        self.PLOT_USING[using](logs, ncols, figsize, xlabel, smooth_perc, dfs, nrows)
        
    def __scalar_plt(
        self,
        logs: list[str], 
        ncols: int,
        figsize: tuple[int, int],
        xlabel: str,
        smooth_perc: float,
        dfs: pd.DataFrame,
        nrows: int,
    ) -> None:
        
        """
        Plot scalar logs over timesteps using Matplotlib.
        """
        
        plt.figure(figsize=figsize)
        for i, log in enumerate(logs):
            ax = plt.subplot(nrows, ncols, i+1)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(log)
            for name in self.log_names:
                ax.plot(dfs.loc[name, log].dropna().ewm(alpha=1-smooth_perc).mean(), label=name)
            ax.legend(loc="upper left")
        plt.show()
        
    def __scalar_plotly(
        self,
        logs: list[str],
        ncols: int,
        figsize: tuple[int, int],
        xlabel: str,
        smooth_perc: float,
        dfs: pd.DataFrame,
        nrows: int,
    ) -> None:
        
        """
        Plot scalar logs over timesteps using Plotly.
        """

        fig = make_subplots(rows=nrows, cols=ncols)
        for i, log in enumerate(logs):
            for name in self.log_names:
                col=(i%ncols)+1; row=(i//ncols)+1
                log_df = dfs.loc[name, log].dropna().ewm(alpha=1-smooth_perc).mean()
                fig.add_trace(go.Scatter(
                        x=log_df.index, y=log_df.to_list(),
                        name=name,
                        showlegend=False,
                    ), row=row, col=col)
            fig.update_xaxes(title_text=xlabel, row=row, col=col)
            fig.update_yaxes(title_text=log, row=row, col=col)
        fig.update_layout(width=figsize[0], height=figsize[1])
        fig.show()
        