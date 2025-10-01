#!/usr/bin/env python3

import pandas as pd
import os
import re
import argparse
from collections import OrderedDict
from datetime import datetime, date

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='OpenShift Day 2 Operator Search Tool - Search for product releases',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                                    # Use default files
  %(prog)s -c mydata.csv -s operators.txt    # Specify custom input files
  %(prog)s --show-all                        # Show all releases, not just future ones
  %(prog)s --no-version-filter               # Disable version filtering
  %(prog)s -o custom_results.txt             # Specify custom output file
        '''
    )
    
    parser.add_argument(
        '-c', '--csv-file',
        dest='csv_file',
        default=None,
        help='Path to CSV file (default: auto-detect Product-Pages-Export-*.csv or first .csv file)'
    )
    
    parser.add_argument(
        '-s', '--source-file',
        dest='source_file',
        default='source.txt',
        help='Path to source file containing operator-product mappings (default: source.txt)'
    )
    
    parser.add_argument(
        '-r', '--reference-file',
        dest='reference_file',
        default='reference.txt',
        help='Path to reference file containing version filters (default: reference.txt)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        default='results.txt',
        help='Path to output file (default: results.txt)'
    )
    
    parser.add_argument(
        '--show-all',
        action='store_true',
        help='Show all releases, not just future ones'
    )
    
    parser.add_argument(
        '--no-version-filter',
        action='store_true',
        help='Disable version filtering from reference.txt'
    )
    
    return parser.parse_args()

def load_csv_data(csv_file=None):
    try:
        if csv_file:
            print(f"Loading: {csv_file}")
            df = pd.read_csv(csv_file)
            print(f"Loaded {len(df)} records")
            return df
        else:
            product_pages_files = [f for f in os.listdir('.') if f.startswith('Product-Pages-Export') and f.endswith('.csv')]
            if product_pages_files:
                csv_file = product_pages_files[0]
            else:
                csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
                if not csv_files:
                    print("Error: No CSV file found")
                    return None
                csv_file = csv_files[0]
            
            print(f"Loading: {csv_file}")
            
            df = pd.read_csv(csv_file)
            print(f"Loaded {len(df)} records")
            return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def load_reference_versions(reference_file='reference.txt'):
    """Load reference versions from reference.txt and create a mapping"""
    version_map = {}
    try:
        if not os.path.exists(reference_file):
            print(f"Warning: {reference_file} not found, no version filtering will be applied")
            return version_map
        
        with open(reference_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        for line in lines:
            # Parse lines like "OCP 4.20", "ACM 2.15", "Quay 3.15", "ODF 4.20"
            parts = line.split()
            if len(parts) >= 2:
                product_abbr = parts[0].upper()
                version = parts[1]
                
                # Map abbreviations to full product names
                if product_abbr == "OCP":
                    version_map["Red Hat OpenShift Container Platform"] = version
                elif product_abbr == "ACM":
                    version_map["Red Hat Advanced Cluster Management for Kubernetes"] = version
                elif product_abbr == "QUAY":
                    version_map["Red Hat Quay"] = version
                elif product_abbr == "ODF":
                    version_map["Red Hat OpenShift Data Foundation"] = version
        
        print(f"Loaded {len(version_map)} version filters from {reference_file}")
        return version_map
        
    except Exception as e:
        print(f"Error loading {reference_file}: {e}")
        return version_map

def load_search_items(source_file='source.txt'):
    try:
        if not os.path.exists(source_file):
            print(f"Error: {source_file} not found")
            return []
        
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        items = []
        for i, line in enumerate(lines):
            if i == 0 and line.startswith('Operator'):
                continue
                
            # Split by tab to get operator, product, and release name
            parts = line.split('\t')
            if len(parts) >= 3:
                operator = re.sub(r'^\d+\.\s*', '', parts[0].strip())
                product = parts[1].strip()
                release_name = parts[2].strip()
                if operator and product and release_name:
                    items.append((operator, product, release_name))
            elif len(parts) >= 2:
                operator = re.sub(r'^\d+\.\s*', '', parts[0].strip())
                product = parts[1].strip()
                if operator and product:
                    items.append((operator, product, ""))
            else:
                operator = re.sub(r'^\d+\.\s*', '', parts[0].strip())
                if operator:
                    items.append((operator, "", ""))
        
        print(f"Loaded {len(items)} operator-product mappings from {source_file}")
        return items
        
    except Exception as e:
        print(f"Error loading {source_file}: {e}")
        return []

def search_by_product(df, product_name, release_name=None):
    if not product_name:
        return pd.DataFrame()
    
    # If a specific release name is provided, try searching by that first
    if release_name:
        release_matches = df[df['Release'].astype(str).str.contains(re.escape(release_name), case=False, na=False)]
        if not release_matches.empty:
            return release_matches
    
    # Search by product name across multiple columns
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
    matches['GA date'] = pd.to_datetime(matches['GA date'])
    future_matches = matches[matches['GA date'].dt.date > today]
    
    return future_matches

def filter_by_version(matches, product_name, version_map):
    """Filter releases to only show those matching the version in reference.txt"""
    if matches.empty or not version_map or product_name not in version_map:
        return matches
    
    target_version = version_map[product_name]
    version_matches = matches[matches['Release'].astype(str).str.contains(re.escape(target_version), case=False, na=False)]
    
    return version_matches

def write_to_file_and_print(text, file_handle=None):
    """Write text to both console and file"""
    print(text)
    if file_handle:
        file_handle.write(text + '\n')

def format_results_by_product(operator_product_pairs, df, version_map, output_file='results.txt', show_all=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = date.today()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        header = f"OpenShift Day 2 Operator Search Results - Conan Tool"
        write_to_file_and_print(header, f)
        write_to_file_and_print(f"Generated: {timestamp}", f)
        if show_all:
            write_to_file_and_print(f"Filter: Showing all releases (including past and future)", f)
        else:
            write_to_file_and_print(f"Filter: Only showing releases with GA dates after {today}", f)
        if version_map:
            write_to_file_and_print(f"Version Filter: {', '.join([f'{k}: {v}' for k, v in version_map.items()])}", f)
        write_to_file_and_print("="*80, f)
        write_to_file_and_print("Search Results by Product/Release Mapping (Source.txt Order):", f)
        write_to_file_and_print("="*80, f)
        
        # Group operators by product while preserving order
        product_groups = OrderedDict()
        for item in operator_product_pairs:
            if len(item) == 3:
                operator, product, release_name = item
            else:
                operator, product = item[0], item[1]
                release_name = ""
            
            if product:
                if product not in product_groups:
                    product_groups[product] = []
                product_groups[product].append((operator, release_name))
        
        # Track operators with and without answers
        operators_with_answers = []
        operators_without_answers = []
        
        products_with_releases = []
        products_without_releases = []
        
        for product, operator_tuples in product_groups.items():
            all_matches = pd.DataFrame()
            operators_list = []
            
            for operator, release_name in operator_tuples:
                operators_list.append(operator)
                operator_matches = search_by_product(df, product, release_name)
                if not operator_matches.empty:
                    all_matches = pd.concat([all_matches, operator_matches]).drop_duplicates()
            
            matches = all_matches
            operators = operators_list
            
            if not matches.empty:
                # Apply version filtering first if available
                if version_map:
                    matches = filter_by_version(matches, product, version_map)
                
                if not matches.empty:
                    # Create a copy to avoid SettingWithCopyWarning
                    matches = matches.copy()
                    matches['GA date'] = pd.to_datetime(matches['GA date'])
                    
                    if show_all:
                        # Get the earliest GA date for each release
                        future_matches = matches.loc[matches.groupby('Release')['GA date'].idxmin()]
                    else:
                        # Filter for future releases first
                        future_only = filter_future_releases(matches)
                        
                        if not future_only.empty:
                            # Get the earliest future GA date for each release
                            future_matches = future_only.loc[future_only.groupby('Release')['GA date'].idxmin()]
                        else:
                            future_matches = pd.DataFrame()
                    
                    if not future_matches.empty:
                        products_with_releases.append((product, operators, future_matches))
                        operators_with_answers.extend(operators)
                    else:
                        products_without_releases.append((product, operators))
                        operators_without_answers.extend(operators)
                else:
                    products_without_releases.append((product, operators))
                    operators_without_answers.extend(operators)
            else:
                products_without_releases.append((product, operators))
                operators_without_answers.extend(operators)
        
        # Add unmapped operators to those without answers
        unmapped_operators = []
        for item in operator_product_pairs:
            if len(item) == 3:
                operator, product, release_name = item
            else:
                operator, product = item[0], item[1]
            if not product:
                unmapped_operators.append(operator)
        operators_without_answers.extend(unmapped_operators)
        
        if products_with_releases:
            if show_all:
                section_header = "\nPRODUCTS WITH RELEASES FOUND"
            else:
                section_header = "\nPRODUCTS WITH FUTURE RELEASES FOUND"
            write_to_file_and_print(section_header, f)
            write_to_file_and_print("="*80, f)
            
            for i, (product, operators, matches_first) in enumerate(products_with_releases, 1):
                write_to_file_and_print(f"\nProduct {i}: {product}", f)
                write_to_file_and_print(f"Operators: {', '.join(operators)}", f)
                write_to_file_and_print("-" * 60, f)
                
                # Sort releases by GA date and take only the 2 closest
                matches_sorted = matches_first.sort_values('GA date')
                closest_2_releases = matches_sorted.head(2)
                
                if show_all:
                    write_to_file_and_print(f"Found {len(matches_first)} release(s):", f)
                else:
                    write_to_file_and_print(f"Found {len(matches_first)} future release(s):", f)
                for _, row in closest_2_releases.iterrows():
                    write_to_file_and_print(f"  BU: {row['BU']}", f)
                    write_to_file_and_print(f"  Release: {row['Release']}", f)
                    write_to_file_and_print(f"  GA date: {row['GA date'].strftime('%Y-%m-%d')}", f)
                    write_to_file_and_print(f"  GA name: {row['GA name']}", f)
                    maintainer = row.get('Maintainers', '')
                    if pd.isna(maintainer) or maintainer == '':
                        maintainer = 'N/A'
                    write_to_file_and_print(f"  Maintainer: {maintainer}", f)
                    write_to_file_and_print(f"  Link: {row['Link']}", f)
                    write_to_file_and_print(f"  Product: {row['Product']}", f)
                    write_to_file_and_print("  " + "-" * 40, f)
        
        if products_without_releases:
            if show_all:
                section_header = "\nPRODUCTS WITH NO RELEASES"
                status_msg = "No releases found"
            else:
                section_header = "\nPRODUCTS WITH NO FUTURE RELEASES"
                status_msg = f"No future releases found (after {today})"
            write_to_file_and_print(section_header, f)
            write_to_file_and_print("="*80, f)
            
            for i, (product, operators) in enumerate(products_without_releases, 1):
                write_to_file_and_print(f"\nProduct {i}: {product}", f)
                write_to_file_and_print(f"Operators: {', '.join(operators)}", f)
                write_to_file_and_print(f"Status: {status_msg}", f)
                write_to_file_and_print("-" * 60, f)
        
        if unmapped_operators:
            section_header = "\nUNMAPPED OPERATORS"
            write_to_file_and_print(section_header, f)
            write_to_file_and_print("="*80, f)
            write_to_file_and_print("The following operators have no product mapping:", f)
            for i, operator in enumerate(unmapped_operators, 1):
                write_to_file_and_print(f"  {i}. {operator}", f)
            write_to_file_and_print("Status: No product mapping available - cannot search", f)
        
        section_header = "\nSUMMARY"
        write_to_file_and_print(section_header, f)
        write_to_file_and_print("="*80, f)
        write_to_file_and_print(f"Query date: {today}", f)
        write_to_file_and_print(f"Products with releases: {len(products_with_releases)}", f)
        write_to_file_and_print(f"Products with no releases: {len(products_without_releases)}", f)
        write_to_file_and_print(f"Unmapped operators: {len(unmapped_operators)}", f)
        write_to_file_and_print(f"Total releases found: {sum(len(matches) for _, _, matches in products_with_releases)}", f)
        write_to_file_and_print(f"Total products analyzed: {len(product_groups)}", f)
        
        write_to_file_and_print("\nOperator Answer Breakdown:", f)
        write_to_file_and_print("-" * 40, f)
        write_to_file_and_print(f"Operators with releases: {len(operators_with_answers)}", f)
        write_to_file_and_print(f"Operators without releases: {len(operators_without_answers)}", f)
        write_to_file_and_print(f"Total operators analyzed: {len(operators_with_answers) + len(operators_without_answers)}", f)
        
        write_to_file_and_print("\nProduct Operator Breakdown:", f)
        write_to_file_and_print("-" * 40, f)
        for product, operators in product_groups.items():
            write_to_file_and_print(f"{product}: {len(operators)} operators", f)
        
        write_to_file_and_print("\n" + "="*80, f)
        write_to_file_and_print("Report generated by OpenShift Day 2 Operator Search Tool - Conan", f)
        if show_all:
            write_to_file_and_print("Filter applied: All releases (past and future)", f)
        else:
            write_to_file_and_print(f"Filter applied: Only releases after {today}", f)
        write_to_file_and_print("="*80, f)
    
    print(f"\nResults exported to: {output_file}")
    if show_all:
        print("Showing all releases (past and future)")
    else:
        print(f"Showing only releases after: {today}")

def main():
    args = parse_arguments()
    
    print("Operator to Product/Release Search Tool")
    print("Processing in source.txt file order")
    if args.show_all:
        print("Filter: Showing all releases (past and future)")
    else:
        print(f"Filter: Only showing future releases (after {date.today()})")
    print("="*60)
    
    df = load_csv_data(args.csv_file)
    if df is None:
        return
    
    version_map = {}
    if not args.no_version_filter:
        version_map = load_reference_versions(args.reference_file)
    
    operator_product_pairs = load_search_items(args.source_file)
    if not operator_product_pairs:
        return
    
    format_results_by_product(operator_product_pairs, df, version_map, args.output_file, args.show_all)

if __name__ == "__main__":
    main()
