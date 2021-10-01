import pandas as pd
import gspread
import gspread_dataframe as gd


def import_worksheet(google_spreadsheet, google_worksheet):
    """
    Imports a google worksheet and saves it as a dataframe.
    
    Args:
        google_spreadsheet: A string representing the target google spreadsheet name.
        google_worksheet: A string representing the target google worksheet name.
        
    Returns:
        target_df: A dataframe containing data from the target google worksheet.
    """
    
    #authenticate gspread
    gc = gspread.oauth()

    #import worksheet
    data_worksheet = gc.open(google_spreadsheet).worksheet(google_worksheet)
    
    #import worksheet data to dataframe
    target_df = gd.get_as_dataframe(data_worksheet)
    
    #remove null rows
    target_df = target_df.dropna(how='all')
    
    #remove null columns
    new_columns = list(filter(lambda column: True if 'Unnamed' not in column else False, target_df.columns))
    target_df = target_df[new_columns]
    
    return target_df


def export_worksheet(google_spreadsheet, google_worksheet, target_df):
    """
    Exports data from a dataframe onto a google worksheet on a particular spreadsheet.
    
    Args:
        google_spreadsheet: A string representing the target google spreadsheet name.
        google_worksheet: A string representing the target google worksheet name.
        target_df: A dataframe containing data to load ont the target google worksheet.
    
    Returns:
        N/A
    """
    
    #authenticate gspread
    gc = gspread.oauth()

    #import worksheet
    data_worksheet = gc.open(google_spreadsheet).worksheet(google_worksheet)
    
    #export cohort file ids
    gd.set_with_dataframe(data_worksheet, target_df)
    
    return
