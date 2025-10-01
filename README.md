# OpenShift Day 2 Operator Search Tool - Conan

A Red Hat OpenShift Product version search tool that helps analyze Product suites related operator GA dates and information links for analysis.

## Overview

Conan is designed to help Red Hat OpenShift administrators and engineers quickly find release information for Day 2 operators across different product suites. It provides detailed information including Business Unit (BU), Release versions, GA dates, and direct links to product pages. The tool now includes advanced version filtering capabilities to match specific product versions.

## Requirements

- **Access to Red Hat Product Pages**: https://productpages.redhat.com/
- **Python 3.7+**
- **Virtual Environment** (recommended)

## Repository Structure

```
Openshift-Day-2-Operator-conan/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── search_releases.py           # Main search script
├── source.txt                   # Day 2 operators and product suite mappings
├── reference.txt                # Target versions (OCP, ACM, Quay, ODF)
└── .gitignore                   # Git ignore rules
```

## File Descriptions

### 📄 **source.txt**
Contains the comprehensive list of Day 2 operators mapped to their respective Red Hat Product suites:
- **Format**: `operator-name<TAB>Product Suite Name<TAB>Release Name`
- **3-Column Structure**: 
  - Column 1: Operator name (e.g., `advanced-cluster-management`)
  - Column 2: Product Suite Name (e.g., `Red Hat Advanced Cluster Management for Kubernetes`)
  - Column 3: Release Name (e.g., `Red Hat Advanced Cluster Management for Kubernetes 2.15`)
- **Coverage**: 35 operators across multiple product suites including:
  - Red Hat OpenShift Data Foundation
  - Red Hat Advanced Cluster Management for Kubernetes
  - Red Hat OpenShift Container Platform
  - Red Hat OpenShift Networking
  - Red Hat OpenShift Logging
  - And more...

### 📄 **reference.txt**
Contains the target product versions used as reference filters. The tool will only show releases matching these versions:
```
OCP 4.20
ACM 2.15
Quay 3.16
ODF 4.20
```
**Purpose**: When specified, the tool filters results to show only releases matching these specific versions, allowing you to focus on your target platform versions.

### 📄 **requirements.txt**
Includes all software packages required to execute the tool:
- `pandas>=2.0.0` - Data manipulation and analysis
- `requests>=2.31.0` - HTTP library for additional utilities

### 🐍 **search_releases.py**
Main Python script that searches for Day 2 operator release information including:
- **BU** (Business Unit)
- **Release** (Version information)
- **GA Date** (General Availability date)
- **GA Name** (Specific release name)
- **Maintainer** (Product maintainer information)
- **Link** (Direct link to product pages)
- **Product** (Product suite name)

**Key Features**:
- Searches by Release Name first (Column 3 in source.txt) for precise matching
- Falls back to Product Suite search if no Release Name match found
- Applies version filtering based on reference.txt
- Shows only future releases (after current date)
- Displays the 2 closest upcoming releases per product

### 📄 **results.txt** (Generated)
Output file containing the search results. **Note**: This file is automatically excluded from Git commits due to privacy considerations.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/mgonzalezo/Openshift-Day-2-Operator-conan.git
cd Openshift-Day-2-Operator-conan
```

### 2. Download Product Data

1. Access the **"Reports"** section at https://productpages.redhat.com/
2. Navigate to the **"Exports"** section
3. Select **"Google Sheets Export"**
4. Download the **CSV file** to the same folder as this repository (the tool now uses CSV format for better performance)

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Execute the Search Tool

```bash
python search_releases.py
```

## Usage

The tool will automatically:

1. **Load** the downloaded CSV file from Red Hat Product Pages
2. **Parse** the operator-to-product mappings from `source.txt` (including Release Name for precise matching)
3. **Apply** version filtering based on `reference.txt` to match your target platform versions
4. **Filter** results to show only future releases (after current date)
5. **Group** operators by their product suites
6. **Display** the closest 2 releases per product suite for focused analysis
7. **Export** results to `results.txt` for offline review

### Version Filtering

The tool uses `reference.txt` to filter releases by version:
- If `reference.txt` contains `OCP 4.20`, only OpenShift Container Platform 4.20 releases will be shown
- If `reference.txt` contains `ACM 2.15`, only ACM 2.15 releases will be shown
- This helps focus on specific product versions relevant to your deployment

### Release Name Matching

The tool first searches using the specific Release Name (Column 3 in `source.txt`):
- Example: `Red Hat Advanced Cluster Management for Kubernetes 2.15`
- This provides more precise matching than searching by Product Suite alone
- If no Release Name is specified, it falls back to Product Suite search

## Sample Output

```
PRODUCTS WITH FUTURE RELEASES FOUND
================================================================================

Product 1: Red Hat OpenShift Data Foundation
Operators: ceph-csi-operator, mcg-operator, ocs-operator, odf-operator, ...
------------------------------------------------------------
Found 8 future release(s), showing closest 2:
  BU: Storage
  Release: Red Hat OpenShift Data Foundation 4.20
  GA date: 2026-01-05
  GA name: odf-4.20.2
  Maintainer: asriram (Anjana Sriram)
  Link: http://productpages.redhat.com/odf-4.20/people/
  Product: Red Hat OpenShift Data Foundation
  ----------------------------------------
  BU: Storage
  Release: Red Hat OpenShift Data Foundation 4.17
  GA date: 2026-03-17
  GA name: Maintenance Phase
  Maintainer: asriram (Anjana Sriram)
  Link: http://productpages.redhat.com/odf-4.17/people/
  Product: Red Hat OpenShift Data Foundation
  ----------------------------------------

SUMMARY
================================================================================
Query date: 2025-09-29
Products with future releases: 7
Products with no future releases: 6
Total future releases found: 25
Total operators analyzed: 35
```

## Supported Product Suites

- **Red Hat OpenShift Data Foundation** (10 operators)
- **Red Hat Advanced Cluster Management for Kubernetes** (2 operators)
- **Red Hat OpenShift Container Platform** (4 operators)
- **Red Hat OpenShift Platform** (8 operators)
- **Red Hat OpenShift Logging** (2 operators)
- **Red Hat OpenShift Service Mesh** (2 operators)
- **Red Hat Quay** (1 operator)
- **Red Hat OpenShift GitOps** (1 operator)
- **Red Hat OpenShift API for Data Protection** (1 operator)
- **Red Hat Build of Keycloak** (1 operator)
- **Red Hat OpenShift Distributed Tracing Platform** (1 operator)
- **Observability** (1 operator)
- **OpenShift Platform** (1 operator)

## Features

- ✅ **Version Filtering**: Filter releases by specific product versions using reference.txt
- ✅ **Precise Release Matching**: Search by specific Release Name for accurate results
- ✅ **Product Suite Grouping**: Automatically groups operators by their product suites
- ✅ **Future Release Filtering**: Shows only releases with GA dates after the current date
- ✅ **Closest Release Priority**: Displays the 2 closest releases per product for focused analysis
- ✅ **Comprehensive Information**: Includes BU, Release, GA Date, GA Name, Maintainer, and Links
- ✅ **CSV Processing**: Optimized for CSV file format for better performance
- ✅ **Privacy Protection**: Results are automatically excluded from Git commits
- ✅ **Detailed Statistics**: Provides comprehensive summary and breakdown information
- ✅ **Comprehensive Coverage**: Supports 35 Day 2 operators across 13+ product suites
- ✅ **Flexible Search**: Falls back from Release Name to Product Suite search automatically

## Troubleshooting

### Common Issues

1. **"No CSV file found"**
   - Ensure you've downloaded the CSV export from Red Hat Product Pages
   - Verify the file is in the same directory as the script
   - The tool looks for files starting with "Product-Pages-Export"

2. **"No future releases found"**
   - The tool only shows releases with GA dates after the current date
   - Check that the data contains upcoming releases for your operators
   - Verify the version filter in reference.txt matches available releases

3. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

4. **Version filtering not working**
   - Check reference.txt format: `PRODUCT_ABBR VERSION` (e.g., `OCP 4.20`)
   - Supported abbreviations: OCP, ACM, QUAY, ODF
   - Ensure the version matches what's in the CSV data

5. **Missing reference.txt**
   - The tool will run without reference.txt but won't apply version filtering
   - A warning will be displayed: "reference.txt not found, no version filtering will be applied"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue in this repository
- Check the Red Hat Product Pages documentation at https://productpages.redhat.com/

---

**Note**: This tool requires access to Red Hat Product Pages and is intended for Red Hat customers and partners with appropriate access credentials. 