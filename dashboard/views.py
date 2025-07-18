from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
import os
import pandas as pd
import io

UPLOAD_DIR = os.path.join('dashboard', 'output')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def index(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'sales':
            return redirect('upload')
        elif role == 'supervisor':
            return redirect('results')
        elif role == 'admin':
            return HttpResponse("Admin Panel coming soon!", status=200)
    return render(request, 'dashboard/index.html')

def upload(request):
    if request.method == 'POST':
        sales_file = request.FILES.get('sales')
        routes_file = request.FILES.get('routes')
        target_file = request.FILES.get('target')

        if not all([sales_file, routes_file, target_file]):
            return HttpResponse("Missing one or more files.", status=400)

        # Read files
        sales_df = pd.read_excel(sales_file)
        routes_df = pd.read_excel(routes_file)
        target_df = pd.read_excel(target_file)

        # Merge logic
        merged_df = sales_df.merge(target_df[["store_type_id", "store_target"]], on='store_type_id', how='left')
        merged_df = merged_df.merge(target_df[["SKU", "SKU_target"]], on='SKU', how='left', suffixes=('_store', '_sku'))

        merged_df['fulfillment_store'] = (merged_df['order_value'] / merged_df['store_target']) * 100
        merged_df['fulfillment_sku'] = (merged_df['order_value'] / merged_df['SKU_target']) * 100

        merged_df['next_target_store'] = merged_df['store_target'] + ((100 - merged_df['fulfillment_store']) / 100) * merged_df['store_target']
        merged_df['next_SKU_target'] = merged_df['SKU_target'] + ((100 - merged_df['fulfillment_sku']) / 100) * merged_df['SKU_target']

        # Save to Excel
        output_path = os.path.join(UPLOAD_DIR, 'processed_target.xlsx')
        merged_df.to_excel(output_path, index=False)

        return redirect(request, 'dashboard/upload_success.html')

    return render(request, 'dashboard/upload.html')

def results_view(request):
    file_path = os.path.join(UPLOAD_DIR, 'processed_target.xlsx')
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        html_table = df.to_html(classes="table", index=False)
        return render(request, 'dashboard/results.html', {'table': html_table})
    return HttpResponse("No processed data found.", status=404)

def download_report(request, filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(open(filepath, 'rb'), as_attachment=True)
    return HttpResponse("File not found", status=404)

def home_page(request):
    return render(request, 'dashboard/index.html')
import logging
logger = logging.getLogger(__name__)
logger.warning("Reached upload view")
