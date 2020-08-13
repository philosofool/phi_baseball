import pandas as pd

"""
Contains functions and classes for handling Marcel Projections as proposed by Tom Tango.

See his webpage (http://www.tangotiger.net/archives/stud0346.shtml). See Tango's comment #28 for pitcher details.

WARNING: The directory structure in phi_baseball is note final. File locations may change.

Classes
-------

MarcelForecaster
    Creates Marcel Forecasts for baseball players. This is a stable release and the API
    will be compatible with future versions; current file/directory location in phi_baseball
    may be subject to change.

"""

class MarcelForecaster:
    """
    Creates Marcel Forecasts for baseball players. 
    
    Attributes
    ----------
    pitchers: DataFrame
        Pitcher stats from which Marcels can be calculated.
        
    hitters: DataFrame
        Hitter stats from which Marcels can be calculated.
        
    hitter_stat_cols: list_like
        The labels of the numeric columns (besides playerid and Season) which
        are forcast in the system. Extracted from hitters by default.
    
    pitcher_stat_cols: list_like
        The labels of the numeric columsn (besides playerid and Season) which
        are forcast in the system. Extracted from pitchers by default.
        
    Class Attributes
    ----------------
    default_hitter: Series
        Default values that can be used as expected values for regression of hitters. 
        
        Useful for working with incomplete data that would skew expected values if it 
        were used to generate expected values. The value included with this package
        is a 5/4/3 weighting of 2019,2018, and 2017 and includes ~2.6% pitchers .
        
    default_pitcher: Series
        Default values that can be used as expected values for regression of pitchers. 
        
        Useful for working with incomplete data that would skew expected values if it 
        were used to generate expected values. The value included with this package is a 
        5/4/3 weighting of 2018, 2018 and 2017. It merges both relievers and starters.
        
    Methods
    -------
    
    project_pitchers(season)
        Creates a set of pitcher Marcels from self.pitchers for the given season.
        
    project_hitters(season)
        Creates a set of hitter Marcels from self.hitters for the given season.
    
    """
    default_hitter = pd.Series( {'Season': 2018.1666666666667,
                        'G': 51.51177353805377,
                        'AB': 119.71508052446381,
                        'PA': 133.9807606888398,
                        'H': 30.109325557433724,
                        '1B': 18.985583962330328,
                        '2B': 6.064403346739954,
                        '3B': 0.5830666616544498,
                        'HR': 4.476271586708993,
                        'R': 16.32033556217925,
                        'RBI': 15.589974443437582,
                        'BB': 11.40276845277441,
                        'IBB': 0.6256480181445081,
                        'SO': 29.998066348656,
                        'HBP': 1.3754344554637221,
                        'SF': 0.8533821082483682,
                        'SH': 0.5985380352063702,
                        'GDP': 2.5592693878197363,
                        'SB': 1.7369829381732262,
                        'CS': 0.6493756891466893,
                        'AVG': 0.13013461925019312,
                        'playerid': 11776.34455945105}
                    )
    
    default_pitcher = pd.Series( {'Season': 2018.1666666666667,
                                     'W': 3.0367303071680873,
                                     'L': 3.0367303071680873,
                                     'ERA': 5.847070224491219,
                                     'G': 26.381013513566757,
                                     'GS': 6.073460614336175,
                                     'CG': 0.059621503114338927,
                                     'ShO': 0.02990347444244394,
                                     'SV': 1.5010360504908942,
                                     'HLD': 3.1259730273385693,
                                     'BS': 0.8077962867471701,
                                     'IP': 54.01530616395814,
                                     'TBF': 232.11361310712672,
                                     'H': 52.16922028963712,
                                     'R': 28.267709217301455,
                                     'ER': 26.200651000332446,
                                     'HR': 7.749032043428635,
                                     'BB': 19.755219561851067,
                                     'IBB': 1.086317006102944,
                                     'HBP': 2.380395861422784,
                                     'WP': 2.2663944934634954,
                                     'BK': 0.1910347156856312,
                                     'SO': 51.94216290973079,
                                     'playerid': 11982.895321932285}
                                )

    def __init__(self,pitcher_data,hitter_data, as_pandas = False):
        """
        Parameters
        ----------
        
        pitcher_data: csv or DataFrame
            A csv or DataFrame containing single season performances by players. The included
            stats columns are the ones that are forecast.
            
            The stats contained can be arbitrary pitching stats, except:
            --Total batters faced must be included and the column should be labeled "TBF"
            --Innings pitched must be included and the columns should be labeled "IP"
            --Columns labeled 'GS' and 'G' must be included. These are used for playtime 
              projection of relievers and starters. If you don't have this data at hand, simply
              including 1 as GS for every starter and 0 as GS for every reliver and 1 as G for both
              will achieve more or less the desired result.
            --The season must be included and the column should be labeled "Season";
              The data from seasons should be integer type.
            --Each row should represent a full season of the player's performance.
            --A column with a playerid that is unique to each player (Fangraphs includes such
              a column in every CSV that you can download from them.)
        
        hitter_data: csv or DataFrame
            A csv or DataFrame containing single season performances by players. The included
            stats columns are the ones that are forecast.
            
            The stats contained can be arbitrary hitting stats, except:
            --Total plate appearances must be included and the column should be labeled "PA"
            --The season must be included and the column should be labeled "Season";
              The data from seasons should be integer type.
            --Each row should represent a full season of the player's performance.
            --A column with a playerid that is unique to each player (Fangraphs includes such
              a column in every CSV that you can download from them.)
              
        as_pandas: bool
            If true, the constructor treats pitcher_data and hitter data as Pandas DataFrames. If false,
            the data is assumed to be a csv file and pd.read_csv will be called on pitcher data and hitter data.


        """
        if as_pandas:
            self.pitchers = pitcher_data
            self.hitters = hitter_data
        else:
            self.pitchers = pd.read_csv(pitcher_data)
            self.hitters = pd.read_csv(hitter_data)
            
        self.hitter_stat_cols = ( 
            self.hitters
            .select_dtypes(include=['float','int','int64','float64','int32','float32'])
            .columns
        )
        self.hitter_stat_cols = self.hitter_stat_cols.drop(
            [x for x in ['Season','playerid','Age'] if x in self.hitter_stat_cols])

        self.pitcher_stat_cols = (
            self.pitchers
            .select_dtypes(include=['float','int','int64','float64','int32','float32'])
            .columns
            
        )
        self.pitcher_stat_cols = self.pitcher_stat_cols.drop(
            [x for x in ['Season','playerid','Age'] if x in self.pitcher_stat_cols])

        self._init_hitter_cols = self.hitters.columns#used to return columns in their original order.
        self._init_pitchers_cols = self.pitchers.columns#used to return columns in their original order.
        
        self.set_bad_hitting_stats(['SO','CS','GDP','SH'])
        ##['W', 'L', 'ERA', 'G', 'GS', 'CG', 'ShO', 'SV', 'HLD', 'BS', 'IP', 'TBF',
        ##'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'HBP', 'WP', 'BK', 'SO', 'FIP',
        ##'K/9', 'BB/9']
        self.set_bad_pitching_stats(['BB','IBB','HBP','ER','R','HR','H','L'])
        
    def add_hitter_data(self,data, as_pandas = False):
        """
        Adds additional data to the hitter data. Useful if you have separate files for each
        relevant year, position, team, etc.
        
        Parameters
        ----------
        data: csv of DataFrame
            The data to add. Must have the same column labels as initial hitter data,
            but no error is raised if not.
            
        as_pandas: bool (default=False)
            Whether to handle the input data as a DataFrame (if True) or csv (if False.)
        """
        if not as_pandas:
            data = pd.read_csv(data)
        self.hitters = pd.concat(self.hitters, data)
        
    def add_pitcher_data(self,data, as_pandas = False):
        """
        Adds additional data to the hitter data. Useful if you have separate files for each
        relevant year, position, team, etc.
        
        Parameters
        ----------
        data: csv of DataFrame
            The data to add. Must have the same column labels as initial hitter data,
            but no error is raised if not.
            
        as_pandas: bool (default=False)
            Whether to handle the input data as a DataFrame (if True) or csv (if False.)
        """
        if not as_pandas:
            data = pd.read_csv(data)
        self.pitchers = pd.concat(self.pitchers, data)
        
    def pitcher_mean_from_data(self,stat):
        ''' 
        Returns the mean value for the stat based on existing data. Use for pitcher data.
        '''
        return self.pitchers[stat].mean()
    
    def hitter_mean_from_data(self,stat):
        """
        Returns the mean value for the stat base on existing data. Use for hitter data.
        """
        return self.hiters[stat].mean()
    
    def expected_mean_hitter(self,season, use_default = False):
        """
        Returns a series which is the weighted mean of hitters in self.hitters or a default
        
        Parameters
        ----------
        season: int
            The season for which an expected mean is desired.
            
        use_default: bool
            If true, uses the default hitter assigned to self.default_hitter. If false,
            calculates the mean from the data in self.hitters.
            
        """
        if use_default:
            return self.default_hitter
        else:
            grouped = self.hitters.groupby('Season')
            s1 = grouped.get_group(season-1).mean()*5
            s2 = grouped.get_group(season-2).mean()*4
            s3 = grouped.get_group(season-3).mean()*3
            out = (s1 + s2 + s3)/12
            return out
    
    def expected_mean_pitcher(self,season, use_default = False):
        """.drop(['Season','playerid','Age'])
        Returns a series which is the weighted mean of pitchers in self.pitchers or a default
        
        Parameters
        ----------
        season: int
            The season for which an expected mean is desired.
            
        use_default: bool.drop(['Season','playerid','Age'])
            If true, uses the default pitcher assigned to self.default_pitcher. If false,
            calculates the mean from the data in self.pitchers.
            
        """
        if use_default:
            return self.default_pitcher
        else:
            grouped = self.pitchers.groupby('Season')
            s1 = grouped.get_group(season-1).mean()*5
            s2 = grouped.get_group(season-2).mean()*4
            s3 = grouped.get_group(season-3).mean()*3
            out = (s1 + s2 + s3)/12
            return out
    
    @staticmethod
    def set_hitter_rates(df):
        """
        Adds (or sets) a column for AVG, SLG, OBP and OPS.
        
        The system assumes that any numeric data is a countable stat to allow
        for arbitrary inputs; these common rate stats are automatically included 
        if the necessary counting stats are present with the presumed column names.
        
        Required column names:
        AVG: H*, AB
        SLG: 1B, 2B, 3B, HR, AB
        OBP: H*, BB, HBP, PA
        OPS: calculated if SLG and OBP are.
        
        *Hits can be calculated from hit types used for SLG or given in a column labeled 'H'
        """
        try:
            hits = df['H']
        except KeyError:
            hits = df['1B']+ df['2B'] + df['3B'] + df['HR']
        except KeyError:
            pass
        try:
            df['AVG'] = hits/df['AB']
        except KeyError:
            pass
        try:
            df['SLG'] = (df['1B']+ 2*df['2B'] + 3*df['3B'] + 4*df['HR'])/df['AB']
        except KeyError:
            pass
        try:
            df['OBP'] = (hits + df['BB'] + df['HBP'])/df['PA']
        except KeyError:
            pass
        try:
            df['OPS'] = df['OBP'] + df['SLG']
        except KeyError:
            pass
        
    @staticmethod
    def set_pitcher_rates(df):
        """
        Adds (or sets) a column for ERA, FIP, K/9, BB/9, and WHIP.
        
        The system assumes that any numeric data is a countable stat to allow
        for arbitrary inputs; these common rate stats are automatically included 
        if the necessary counting stats are present with the presumed column names.
        
        Required column names:
        ER, IP, BB, HR, K or SO*, H. 
        
        *K is the preferred for strike outs, but it will attempt SO if no column is named
        K. If SO means shut outs, you're going to have a "Shut Outs per IP" that's labeled 'K/9'
        """
        try:
            df['ERA'] = df['ER']/df['IP']*9
        except KeyError:
            pass
        
        try:
            df['FIP'] = (df['K']*-2+df['BB']*3+df['HR']*13)/df['IP'] + 3.2
        except KeyError:
            df['FIP'] = (df['SO']*-2+df['BB']*3+df['HR']*13)/df['IP'] + 3.2
        except KeyError:
            pass
        
        try:
            df['K/9'] = df['K']/df['IP']*9
        except KeyError:
            df['K/9'] = df['SO']/df['IP']*9
        except KeyError:
            pass
        
        try:
            df['BB/9'] = df['BB']/df['IP']*9
        except KeyError:
            pass

        try:
            df['WHIP'] = (df['K']+df['BB'])/df['IP']
        except KeyError:
            pass
        
        

    def scale_hitter_data(self,row,scaling):
        """
        Returns a players stats given in row scaled to a value; multiplies row by scaling
        """
        x = row[self.hitter_stat_cols]
        row[self.hitter_stat_cols] = x*scaling
        return row
    
    def scale_pitcher_data(self,row,scaling):
        """
        Returns a players stats given in row scaled to a value; multiplies row by scaling
        """
        row[self.pitcher_stat_cols] = row[self.pitcher_stat_cols]*scaling
        return row
    
    def project_hitters(self,season,use_default = False, apply_age = True):
        """
        Return a dataframe of the hitters' Marcel forecasts.
        
        Parameters
        ----------
        
        season: int
            The season for which a projection will be calculated.
            
        use_default: bool (default = False)
            If True, uses self.default_hitter as the expected mean performance for regression. 
            If False, calculates the expected mean performance from the data.
            
        apply_age: bool (default = True)
            Whether to apply an aging curve. Useful if a data set doesn't include ages. 
        """
        df = self._hit_step1(season)
        
        #step 2
        mean_guy = self.expected_mean_hitter(season, use_default = use_default)
        mean_guy = mean_guy.divide(mean_guy['PA'])*1200
        
        #step 3
        df[self.hitter_stat_cols] = (
            df[self.hitter_stat_cols]
            .apply(lambda x: x + mean_guy[self.hitter_stat_cols], axis = 1)
        )
        
        #step 4
        prorating = self._hit_step4_prorating(season)
        df[self.hitter_stat_cols] = df[self.hitter_stat_cols].apply(lambda x: x/x['PA'], axis =1)
        df[self.hitter_stat_cols] = df[self.hitter_stat_cols].apply(lambda x: x*prorating.loc[x.name]['PA'], axis = 1)
        
        #step 5
        ## I honestly don't understand this part of Marcel.
        ## It says to find Age - 29, multiply by .003 or .006 and "apply it to the result of set 4"
        ## Apply how? 
        ## In comments, we see that it's actually 29 - Age, and that it should be "applied"
        ## to everything except PA and AB. I think the ideas is that you multiply by 1 + ageAdj
        ## or 1 - ageAdj (if the stat is "bad", e.g., striking out.)
        
        df = df.apply(self._hit_step5, axis=1)
        
        df['Season'] = season
        df = df[self._init_hitter_cols]
        self.set_hitter_rates(df)
        
        return df
    
    def project_pitchers(self, season, use_default = False):
        """
        Returns a DataFrame of the pitchers' Marcel Forcasts.
        
        Parameters
        ----------
        
        season: int
            The season for which a projection will be calculated.

        use_default: bool (default = False)
            If True, uses self.default_pitcher as the expected mean performance for regression. 
            If False, calculates the expected mean performance from the data.
        """
        df = self._pit_step1(season).copy()
        #step 2
        mean_guy = self.expected_mean_pitcher(season, use_default = use_default)
        mean_guy = mean_guy.divide(mean_guy['TBF'])*1200
        #step 3
        stats = self.pitcher_stat_cols
        df[stats] = df[stats].apply(lambda x: x + mean_guy[stats], axis = 1)
        #step 4
        prorating = self._pit_step4_prorating(season)
        df[stats] = df[stats].apply(lambda x: x/x['IP'], axis = 1)
        df[stats] = df[stats].apply(lambda x: x*prorating.loc[x.name]['IP'], axis=1)
        #step 5
        df = df.apply(self._pit_step5, axis =1)

        df['Season'] = season
        df = df[self._init_pitchers_cols]
        self.set_pitcher_rates(df)
        
        return df
    
    def set_bad_hitting_stats(self, bad_stats):
        """
        Sets which stats increase run scoring for a hitter's team ("good stats") and which reduce it
        ("bad stats".)
        
        These are used when applying the aging curve. By default, any stat (except PA and AB) 
        which is not in bad_stats is assumed to represent an improvement.
        """
        self.hit_bad_stats = [x for x in bad_stats if x in self.hitter_stat_cols]
        self.hit_good_stats = [x for x in self.hitter_stat_cols if x not in self.hit_bad_stats + ['PA','AB']]

    def set_bad_pitching_stats(self, bad_stats):
        """
        Sets which stats reduce run scoring for a pitcher's opponents ("good stats") and which 
        increase it ("bad stats".)
        
        These are used when applying the aging curve. By default, any stat (except PA and AB) 
        which is not in bad_stats is assumed to represent an improvement.
        """
        self.pit_bad_stats = [x for x in bad_stats if x in self.pitcher_stat_cols]
        self.pit_good_stats = [x for x in self.pitcher_stat_cols if x not in self.pit_bad_stats + ['TBF','IP']]
        
    def _pit_step1(self,season):
        """
        Private method. 
        
        Returns a dataframe that gives the 3/2/1 cummulative stats.
        """
        df1 = self.pitchers[self.pitchers['Season'] == season -1]
        df2 = self.pitchers[self.pitchers['Season'] == season -2]
        df3 = self.pitchers[self.pitchers['Season'] == season -3]
        stats = self.pitcher_stat_cols
        df1[stats] = df1[stats]*3
        df2[stats] = df2[stats]*2
        df3[stats] = df3[stats]*1
        
        df = pd.concat([df1,df2,df3])
        
        grouped = df.groupby('playerid')
        apply_dict = {x : 'sum' for x in self.pitcher_stat_cols}
        apply_dict.update({x: 'max' for x in self.pitchers.columns if x not in self.pitcher_stat_cols})
        df = grouped.agg(apply_dict)
        return df
    
    def _pit_step4_prorating(self,season):
        """
        Private method.
        
        Returns DataFrame with the IP proratings.
        """
        df = self.pitchers[['playerid','Name','IP','Season','GS','G']].copy()
        stats = 'IP' #for readability
        df[stats] = df[stats].where(df['Season'] != season -1, df[stats]*.5)
        df[stats] = df[stats].where(df['Season'] != season -2, df[stats]*.1,)
        df[stats] = df[stats].where(((df['Season'] == season -1) | (df['Season'] == season -2)), 0)
        grouped = df[['IP','GS','G','playerid']].groupby('playerid').agg(sum)
        grouped['IP'] = grouped['IP'] + grouped['GS']/grouped['G'] * 60 + (1 - grouped['GS']/grouped['G'])*25
        return grouped

    def _pit_step5(self,row):
        """
        Applies the aging curve to pitchers.
        """
        if row['Age'] >= 29:
            age_adj = .003*(29 - row['Age'])
        else:
            age_adj = .006*(29 - row['Age'])
        row[self.pit_good_stats] = row[self.pit_good_stats].apply(lambda x: x*(1+age_adj))
        row[self.pit_bad_stats] = row[self.pit_bad_stats].apply(lambda x: x*(1-age_adj))
        return row
    
    def _hit_step1(self,season):
        """
        Private method. 
        
        Returns a dataframe that gives the 5/4/3 cummulative stats.
        
        Stats (such as age, season, etc.) are returned as their max.
        """
        df1 = self.hitters[self.hitters['Season'] == season-1].apply(self.scale_hitter_data,
                                                                     args=(5,),
                                                                    axis=1)
        df2 = self.hitters[self.hitters['Season'] == season-2].apply(self.scale_hitter_data,
                                                                     args=(4,),
                                                                    axis=1)
        df3 = self.hitters[self.hitters['Season'] == season-3].apply(self.scale_hitter_data,
                                                                     args=(3,),
                                                                    axis=1)
        df = pd.concat([df1,df2,df3])
        grouped = df.groupby('playerid')
        apply_dict = {x: 'sum' for x in self.hitter_stat_cols}
        apply_dict.update({x: 'max' for x in self.hitters.columns if x not in self.hitter_stat_cols})
        cummulative = grouped.agg(apply_dict)
        return cummulative
    
    
    def _hit_step4_prorating(self,season):
        """
        Private method.
        
        Returns DataFrame with the IP proratings.
        """
        df = self.hitters[['playerid','Name','PA','Season']].copy()
        stats = 'PA' #this was unnecessary, but helpful when I coped this for the pitching equivalent.
        df[stats] = df[stats].where(df['Season'] != season -1, df[stats]*.5)
        df[stats] = df[stats].where(df['Season'] != season -2, df[stats]*.1,)
        df[stats] = df[stats].where(((df['Season'] == season -1) | (df['Season'] == season -2)), 0)
        grouped = df[['PA','playerid']].groupby('playerid').agg(sum)
        grouped['PA'] = grouped['PA'] + 200
        return grouped
    
    def _hit_step5(self, row): 
        """
        The aging curve step. This is applied to the existing dataframe in project hitter
        """
        if row['Age'] >= 29:
            age_adj = .003*(29 - row['Age'])
        else:
            age_adj = .006*(29 - row['Age'])
        row[self.hit_good_stats] = row[self.hit_good_stats].apply(lambda x: x*(1+age_adj))
        row[self.hit_bad_stats] = row[self.hit_bad_stats].apply(lambda x: x*(1-age_adj))
        return row
