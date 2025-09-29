# OpenShift Day 2 Operator Search Tool - Conan

A Red Hat OpenShift Product version search tool that helps analyze Product suites related operator GA dates and information links for analysis.

## Overview

Conan is designed to help Red Hat OpenShift administrators and engineers quickly find release information for Day 2 operators across different product suites. It provides detailed information including Business Unit (BU), Release versions, GA dates, and direct links to product pages.

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
├── reference.txt               # Target versions (OCP, ACM, Quay, ODF)
└── .gitignore                  # Git ignore rules
```

## File Descriptions

### 📄 **source.txt**
Contains the comprehensive list of Day 2 operators mapped to their respective Red Hat Product suites:
- **Format**: `operator-name<TAB>Product Suite Name`
- **Coverage**: 35 operators across multiple product suites including:
  - Red Hat OpenShift Data Foundation
  - Red Hat Advanced Cluster Management for Kubernetes
  - Red Hat OpenShift Platform
  - Red Hat OpenShift Networking
  - Red Hat OpenShift Logging
  - And more...

### 📄 **reference.txt**
Contains the target product versions used as reference filters:
```
OCP 4.20
ACM 2.15
Quay 3.15
ODF 4.20
```

### 📄 **requirements.txt**
Includes all software packages required to execute the tool:
- `pandas` - Data manipulation and analysis
- `openpyxl` - Excel file processing
- `re` - Regular expressions (built-in)

### 🐍 **search_releases.py**
Main Python script that searches for Day 2 operator release information including:
- **BU** (Business Unit)
- **Release** (Version information)
- **GA Date** (General Availability date)
- **Link** (Direct link to product pages)
- **Product** (Product suite name)

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
4. Download the Excel file to the same folder as this repository

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

1. **Load** the downloaded Excel file from Red Hat Product Pages
2. **Parse** the operator-to-product mappings from `source.txt`
3. **Filter** results based on versions in `reference.txt`
4. **Group** operators by their product suites
5. **Display** comprehensive release information for each product suite

## Sample Output

```
🔍 Product: Red Hat OpenShift Data Foundation
Operators: ceph-csi-operator, mcg-operator, ocs-operator, odf-operator, ...
------------------------------------------------------------
✅ Found 13 release(s):
  BU: Storage
  Release: Red Hat OpenShift Data Foundation 4.20
  GA date: 2025-11-06
  Link: http://productpages.redhat.com/odf-4.20/people/
  Product: Red Hat OpenShift Data Foundation
  ----------------------------------------
```

## Supported Product Suites

- **Red Hat OpenShift Data Foundation** (10 operators)
- **Red Hat Advanced Cluster Management for Kubernetes** (2 operators)
- **Red Hat OpenShift Platform** (9 operators)
- **Red Hat OpenShift Networking** (3 operators)
- **Red Hat OpenShift Logging** (2 operators)
- **Red Hat OpenShift Service Mesh** (2 operators)
- **Red Hat Quay** (1 operator)
- **Red Hat OpenShift GitOps** (1 operator)
- **Red Hat OpenShift API for Data Protection** (1 operator)
- **Red Hat Build of Keycloak** (1 operator)
- **Red Hat OpenShift Distributed Tracing Platform** (1 operator)
- **Red Hat OpenShift Monitoring** (1 operator)
- **Red Hat OpenShift Storage** (1 operator)

## Features

- ✅ **Product Suite Grouping**: Automatically groups operators by their product suites
- ✅ **Version Filtering**: Focuses on specific target versions (OCP 4.20, ACM 2.15, etc.)
- ✅ **First GA Date Priority**: Shows only the initial GA date for each release
- ✅ **Direct Links**: Provides direct links to Red Hat Product Pages
- ✅ **Comprehensive Coverage**: Supports 35 Day 2 operators across 13+ product suites

## Troubleshooting

### Common Issues

1. **"No Excel file found"**
   - Ensure you've downloaded the Excel export from Red Hat Product Pages
   - Verify the file is in the same directory as the script

2. **"No data found for specified versions"**
   - Check that `reference.txt` contains the correct version numbers
   - Verify the Excel file contains data for the target versions

3. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

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