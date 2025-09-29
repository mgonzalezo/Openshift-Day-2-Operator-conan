#!/usr/bin/env python3
"""
Release Search Tool
Searches for items from source.txt in the Excel data and returns matching information
"""

import pandas as pd
import os
import sys
import re

def load_excel_data():
    """
    Load the Excel data from the releases sheet
    
    Returns:
        pandas.DataFrame: Excel data or None if error
    """
    try:
        # Find Excel file
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
        if not excel_files:
            print("Error: No Excel file found in directory")
            return None
        
        excel_file = excel_files[0]
        print(f"Loading data from: {excel_file}")
        
        # Load the "Releases GAs" sheet
        df = pd.read_excel(excel_file, sheet_name="Releases GAs")
        print(f"Loaded {len(df)} records from Excel")
        return df
        
    except Exception as e:
        print(f"Error loading Excel data: {e}")
        return None

def load_search_items():
    """
    Load search items from source.txt file
    
    Returns:
        list: List of operator-product pairs
    """
    try:
        if not os.path.exists("source.txt"):
            print("Error: source.txt not found")
            return []
        
        with open("source.txt", 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        items = []
        for line in lines:
            # Split by tab to get operator and product mapping
            parts = line.split('\t')
            if len(parts) >= 2:
                operator = re.sub(r'^\d+\.\s*', '', parts[0].strip())
                product = parts[1].strip()
                if operator and product:
                    items.append((operator, product))
            else:
                # Handle lines without product mapping
                operator = re.sub(r'^\d+\.\s*', '', parts[0].strip())
                if operator:
                    items.append((operator, ""))
        
        print(f"Loaded {len(items)} operator-product mappings")
        return items
        
    except Exception as e:
        print(f"Error loading source.txt: {e}")
        return []

def search_by_product(df, product_name):
    """
    Search for a product in the dataframe and return matching records
    
    Args:
        df (pandas.DataFrame): Excel data
        product_name (str): Product name to search for
        
    Returns:
        pandas.DataFrame: Matching records
    """
    if not product_name:
        return pd.DataFrame()
    
    search_columns = ['Product', 'Release', 'Release shortname', 'Release ID', 'GA name']
    matches = pd.DataFrame()
    
    for col in search_columns:
        if col in df.columns:
            col_matches = df[df[col].astype(str).str.contains(re.escape(product_name), case=False, na=False)]
            matches = pd.concat([matches, col_matches]).drop_duplicates()
    
    return matches

def format_results_by_product(operator_product_pairs, df):
    """
    Format search results for display by product/release mapping
    
    Args:
        operator_product_pairs (list): List of operator-product pairs
        df (pandas.DataFrame): Excel data
    """
    print("Search Results by Product/Release Mapping:")
    print("="*80)
    
    # Group operators by product
    product_groups = {}
    for operator, product in operator_product_pairs:
        if product:
            if product not in product_groups:
                product_groups[product] = []
            product_groups[product].append(operator)
    
    total_found = 0
    
    for product, operators in product_groups.items():
        print(f"\n🔍 Product: {product}")
        print(f"Operators: {', '.join(operators)}")
        print("-" * 60)
        
        # Search for this product in the data
        matches = search_by_product(df, product)
        
        if not matches.empty:
            # Get only first GA date for each release
            matches['GA date'] = pd.to_datetime(matches['GA date'])
            matches_first = matches.loc[matches.groupby('Release')['GA date'].idxmin()]
            
            print(f"✅ Found {len(matches_first)} release(s):")
            for _, row in matches_first.iterrows():
                print(f"  BU: {row['BU']}")
                print(f"  Release: {row['Release']}")
                print(f"  GA date: {row['GA date'].strftime('%Y-%m-%d')}")
                print(f"  Link: {row['Link']}")
                print(f"  Product: {row['Product']}")
                print("  " + "-" * 40)
            
            total_found += len(matches_first)
        else:
            print(f"❌ No releases found for {product}")
    
    # Handle operators without product mapping
    unmapped_operators = [op for op, prod in operator_product_pairs if not prod]
    if unmapped_operators:
        print(f"\n🔍 Unmapped Operators:")
        print(f"Operators: {', '.join(unmapped_operators)}")
        print("-" * 60)
        print("❌ No product mapping available - cannot search")
    
    print(f"\nSummary:")
    print(f"Total products with mappings: {len(product_groups)}")
    print(f"Total releases found: {total_found}")
    print(f"Unmapped operators: {len(unmapped_operators)}")

def main():
    """
    Main function to perform the search
    """
    print("Operator to Product/Release Search Tool")
    print("="*60)
    
    df = load_excel_data()
    if df is None:
        return
    
    operator_product_pairs = load_search_items()
    if not operator_product_pairs:
        return
    
    format_results_by_product(operator_product_pairs, df)

if __name__ == "__main__":
    main() 