# Google Earth Engine (GEE) Authentication for GitHub Actions

This guide explains how to set up authentication for Google Earth Engine (GEE) in a GitHub Actions environment using a service account. This setup is necessary to allow automated workflows, such as the CoastSat pipeline, to access GEE and download satellite images.

## Step 1: Create a Service Account in Google Cloud

1. **Access Google Cloud Console**:
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Make sure you're logged in with your Google account.

2. **Create a New Service Account**:
   - Navigate to **IAM & Admin > Service Accounts**.
   - Click on **Create Service Account**.
   - Provide a name for the service account, e.g., `github-actions-coastsat`.
   - (Optional) Add a description to help identify the account's purpose.
   - Click **Create and Continue**.

3. **Assign Permissions**:
   - Assign the role **Project > Editor** to the service account.
   - (Optional) You can choose a more restrictive role based on your needs.
   - Click **Done**.

4. **Generate a Key for the Service Account**:
   - In the **Service Accounts** list, find the service account you just created.
   - Click on the account to view its details.
   - Navigate to the **Keys** section and click **Add Key > Create New Key**.
   - Select **JSON** as the key type.
   - Click **Create** to download the key file (a `.json` file). **Keep this file secure**.

## Step 2: Add the Service Account Credentials to GitHub

1. **Open Your GitHub Repository**:
   - Navigate to your repository on GitHub.

2. **Access Repository Settings**:
   - Click on **Settings** in the repository menu.
   - Navigate to **Secrets and variables > Actions**.

3. **Add a New Repository Secret**:
   - Click on **New repository secret**.
   - Name the secret `GEE_SERVICE_ACCOUNT`.
   - Open the `.json` key file you downloaded earlier.
   - Copy the entire content of the JSON file and paste it into the **Value** field.
   - Click **Add secret** to save the credentials securely. 

## Step 3: Modify Your GitHub Actions Workflow

Add the following steps to your GitHub Actions workflow file (e.g., `.github/workflows/test.yml`) to authenticate with GEE using the service account:

```yaml
name: Python Tests

on:
  push:
    branches:
      - '**'
  pull_request:
    branches:
      - '**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Miniconda
        uses: conda-incubator/setup-miniconda@v2
        with:
          activate-environment: coastsat-env
          python-version: 3.12

      - name: Recreate Conda Environment
        shell: bash -l {0}
        run: |
          conda deactivate
          conda remove --name coastsat-env --all -y
          conda create --name coastsat-env python=3.12 -y
          conda activate coastsat-env

      - name: Initialize Conda and Install Dependencies
        shell: bash -l {0}
        run: |
          echo "Initializing Conda..."
          conda init bash
          source ~/.bashrc
          echo "Conda initialized."

          echo "Activating the environment..."
          conda activate coastsat-env

          echo "Installing dependencies..."
          conda install -c conda-forge sqlite -y
          conda install -c conda-forge geopandas -y
          conda install -c conda-forge earthengine-api scikit-image matplotlib astropy notebook -y
          pip install pyqt5 imageio-ffmpeg

          echo "Installed packages:"
          conda list
          pip list

      - name: Set up Earth Engine Authentication
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GEE_SERVICE_ACCOUNT }}
        run: |
          echo "$GOOGLE_APPLICATION_CREDENTIALS" > /tmp/gee_credentials.json
          export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gee_credentials.json"
          earthengine authenticate --quiet --earthengine --no-browser --service-account-file=/tmp/gee_credentials.json

      - name: Run Python Test Script
        shell: bash -l {0}
        run: |
          conda activate coastsat-env
          python test.py
