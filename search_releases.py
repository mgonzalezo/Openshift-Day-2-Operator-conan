#!/usr/bin/env python3

import pandas as pd
import os
import sys
import re
from collections import OrderedDict
from datetime import datetime, date

def load_excel_data():
    try:
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
        if not excel_files:
            print("Error: No Excel file found")
            return None
        
        excel_file = excel_files[0]
        print(f"Loading: {excel_file}")
        
        df = pd.read_excel(excel_file, sheet_name="Releases GAs")
        print(f"Loaded {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def load_search_items():
    try:
        if not os.path.exists("source.txt"):
            print("Error: source.txt not found")
            return []
        
        with open("source.txt", 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        items = []
        for i, line in enumerate(lines):
            # Skip header row
            if i == 0 and line.startswith('Operator'):
                continue
                
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
    if not product_name:
        return pd.DataFrame()
    
    search_columns = ['Product', 'Release', 'Release shortname', 'Release ID', 'GA name']
    matches = pd.DataFrame()
    
    for col in search_columns:
        if col in df.columns:
            col_matches = df[df[col].astype(str).str.contains(re.escape(product_name), case=False, na=False)]
            matches = pd.concat([matches, col_matches]).drop_duplicates()
    
    return matches

def filter_future_releases(matches):
    """Filter releases to only show those with GA dates after today"""
    if matches.empty:
        return matches
    
    today = date.today()
    
    # Convert GA date to datetime if not already
    matches['GA date'] = pd.to_datetime(matches['GA date'])
    
    # Filter for future dates only
    future_matches = matches[matches['GA date'].dt.date > today]
    
    return future_matches

def write_to_file_and_print(text, file_handle=None):
    """Write text to both console and file"""
    print(text)
    if file_handle:
        file_handle.write(text + '\n')

def format_results_by_product(operator_product_pairs, df):
    # Open results file for writing
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = date.today()
    
    with open("results.txt", 'w', encoding='utf-8') as f:
        # Write header
        header = f"OpenShift Day 2 Operator Search Results - Conan Tool"
        write_to_file_and_print(header, f)
        write_to_file_and_print(f"Generated: {timestamp}", f)
        write_to_file_and_print(f"Filter: Only showing releases with GA dates after {today}", f)
        write_to_file_and_print("="*80, f)
        write_to_file_and_print("Search Results by Product/Release Mapping (Source.txt Order):", f)
        write_to_file_and_print("="*80, f)
        
        # Group operators by product while preserving order
        product_groups = OrderedDict()
        for operator, product in operator_product_pairs:
            if product:
                if product not in product_groups:
                    product_groups[product] = []
                product_groups[product].append(operator)
        
        # Separate products with and without releases
        products_with_releases = []
        products_without_releases = []
        total_releases_before_filter = 0
        
        for product, operators in product_groups.items():
            matches = search_by_product(df, product)
            
            if not matches.empty:
                # Count total releases before filtering
                matches['GA date'] = pd.to_datetime(matches['GA date'])
                matches_first = matches.loc[matches.groupby('Release')['GA date'].idxmin()]
                total_releases_before_filter += len(matches_first)
                
                # Filter for future releases only
                future_matches = filter_future_releases(matches_first)
                
                if not future_matches.empty:
                    products_with_releases.append((product, operators, future_matches))
                else:
                    products_without_releases.append((product, operators))
            else:
                products_without_releases.append((product, operators))
        
        # Display products WITH future releases found
        if products_with_releases:
            section_header = "\nPRODUCTS WITH FUTURE RELEASES FOUND"
            write_to_file_and_print(section_header, f)
            write_to_file_and_print("="*80, f)
            
            total_found = 0
            for i, (product, operators, matches_first) in enumerate(products_with_releases, 1):
                write_to_file_and_print(f"\nProduct {i}: {product}", f)
                write_to_file_and_print(f"Operators: {', '.join(operators)}", f)
                write_to_file_and_print("-" * 60, f)
                
                write_to_file_and_print(f"Found {len(matches_first)} future release(s):", f)
                for _, row in matches_first.iterrows():
                    write_to_file_and_print(f"  BU: {row['BU']}", f)
                    write_to_file_and_print(f"  Release: {row['Release']}", f)
                    write_to_file_and_print(f"  GA date: {row['GA date'].strftime('%Y-%m-%d')}", f)
                    write_to_file_and_print(f"  Link: {row['Link']}", f)
                    write_to_file_and_print(f"  Product: {row['Product']}", f)
                    write_to_file_and_print("  " + "-" * 40, f)
                
                total_found += len(matches_first)
        
        # Display products WITHOUT future releases found
        if products_without_releases:
            section_header = "\nPRODUCTS WITH NO FUTURE RELEASES"
            write_to_file_and_print(section_header, f)
            write_to_file_and_print("="*80, f)
            
            for i, (product, operators) in enumerate(products_without_releases, 1):
                write_to_file_and_print(f"\nProduct {i}: {product}", f)
                write_to_file_and_print(f"Operators: {', '.join(operators)}", f)
                write_to_file_and_print(f"Status: No future releases found (after {today})", f)
                write_to_file_and_print("-" * 60, f)
        
        # Handle operators without product mapping (in order)
        unmapped_operators = [op for op, prod in operator_product_pairs if not prod]
        if unmapped_operators:
            section_header = "\nUNMAPPED OPERATORS"
            write_to_file_and_print(section_header, f)
            write_to_file_and_print("="*80, f)
            write_to_file_and_print("The following operators have no product mapping:", f)
            for i, operator in enumerate(unmapped_operators, 1):
                write_to_file_and_print(f"  {i}. {operator}", f)
            write_to_file_and_print("Status: No product mapping available - cannot search", f)
        
        # Summary
        section_header = "\nSUMMARY"
        write_to_file_and_print(section_header, f)
        write_to_file_and_print("="*80, f)
        write_to_file_and_print(f"Query date: {today}", f)
        write_to_file_and_print(f"Products with future releases: {len(products_with_releases)}", f)
        write_to_file_and_print(f"Products with no future releases: {len(products_without_releases)}", f)
        write_to_file_and_print(f"Unmapped operators: {len(unmapped_operators)}", f)
        write_to_file_and_print(f"Total future releases found: {sum(len(matches) for _, _, matches in products_with_releases)}", f)
        write_to_file_and_print(f"Total products analyzed: {len(product_groups)}", f)
        
        # Product operator breakdown
        write_to_file_and_print("\nProduct Operator Breakdown:", f)
        write_to_file_and_print("-" * 40, f)
        for product, operators in product_groups.items():
            write_to_file_and_print(f"{product}: {len(operators)} operators", f)
        
        # Footer
        write_to_file_and_print("\n" + "="*80, f)
        write_to_file_and_print("Report generated by OpenShift Day 2 Operator Search Tool - Conan", f)
        write_to_file_and_print(f"Filter applied: Only releases after {today}", f)
        write_to_file_and_print("="*80, f)
    
    print(f"\nResults exported to: results.txt")
    print(f"Showing only releases after: {today}")

def main():
    print("Operator to Product/Release Search Tool")
    print("Processing in source.txt file order")
    print(f"Filter: Only showing future releases (after {date.today()})")
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