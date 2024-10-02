import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def generate_recommendations(df):
    recommendations = []
    for index, row in df.iterrows():
        if row['Biz Revenue Post SB 2'] < row['Biz Expenses Post SB 2']:
            recommendations.append("Financial Management and Budgeting")
        elif row['Biz Inventory Post SB 2'] > row['Biz Revenue Post SB 2'] * 0.5:
            recommendations.append("Inventory Management and Supply Chain Optimization")
        elif row['Biz Revenue Post SB 2'] < row['SB Grant Value Post SB 1']:
            recommendations.append("Marketing and Sales Strategies")
        elif row['Biz Cash Post SB 2'] < row['Biz Revenue Post SB 2'] * 0.2:
            recommendations.append("Cash Flow Management")
        elif row['# Of BOs dropped Post SB 2'] > 0:
            recommendations.append("Member Retention Strategies")
        elif row['Records Kept Post SB 2'] == 'No':
            recommendations.append("Recordkeeping and Compliance")
        elif row['Biz Input Post SB 2'] < row['SB Grant Value Post SB 1'] * 0.1:
            recommendations.append("Effective Utilization of Grants")
        else:
            recommendations.append("General Business Improvement")
    return recommendations

def identify_performance(df):
    performance = []
    for index, row in df.iterrows():
        if row['Biz Revenue Post SB 2'] < row['Biz Expenses Post SB 2']:
            performance.append("Poor Performing")
        else:
            performance.append("Good Performing")
    return performance

def analyze_and_recommend_training(file_path):
    # Load the dataset
    df = pd.read_csv(file_path)

    # Automatically detect numerical and categorical columns
    numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

    # Handle missing values
    df[numerical_columns] = df[numerical_columns].fillna(df[numerical_columns].mean())
    df[categorical_columns] = df[categorical_columns].fillna(df[categorical_columns].mode().iloc[0])

    # Define the preprocessing steps for numerical and categorical data
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    # Create a preprocessor with ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_columns),
            ('cat', categorical_transformer, categorical_columns)
        ])

    # Create a pipeline that first preprocesses the data and then applies PCA
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('pca', PCA(n_components=2))
    ])

    # Apply the pipeline to the data
    principal_components = pipeline.fit_transform(df)

    # Create a DataFrame with the principal components
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])

    # Plot the principal components
    plt.figure(figsize=(10, 7))
    plt.scatter(pca_df['PC1'], pca_df['PC2'], alpha=0.5)
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title('PCA of Business Performance Indicators')
    plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], 'pca_plot.png'))
    plt.close()

    # Print explained variance ratio to understand the importance of each principal component
    pca = pipeline.named_steps['pca']
    print(f"Explained variance ratio: {pca.explained_variance_ratio_}")

    # Apply KMeans clustering to identify groups of businesses with similar performance
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(principal_components)

    # Add the cluster labels to the original dataframe
    df['Cluster'] = clusters

    # Generate dynamic training recommendations based on multiple performance indicators
    df['Training Recommendation'] = generate_recommendations(df)

    # Identify performance of each business
    df['Performance'] = identify_performance(df)

    # Save the dataframe with training recommendations and performance to a new CSV file
    output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'business_training_recommendations.csv')
    df.to_csv(output_file_path, index=False)

    print(f"Training recommendations have been saved to '{output_file_path}'.")

    # Generate a report with key performing business indicators and business per BM cycle
    report = df.groupby('BM Cycle Name').agg({
        numerical_columns[0]: ['mean', 'sum'],
        numerical_columns[1]: ['mean', 'sum'],
        numerical_columns[2]: ['mean', 'sum'],
        numerical_columns[3]: ['mean', 'sum'],
        numerical_columns[4]: ['mean', 'sum'],
        'Business Group Name': 'count'
    }).rename(columns={'Business Group Name': 'Number of Businesses'})

    report.columns = ['_'.join(col).strip() for col in report.columns.values]
    
    report_output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'business_performance_report.csv')
    report.to_csv(report_output_file_path)

    print(f"Business performance report has been saved to '{report_output_file_path}'.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        analyze_and_recommend_training(file_path)
        return redirect(url_for('results'))
    return redirect(request.url)

@app.route('/results')
def results():
    recommendations = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'business_training_recommendations.csv'))
    report = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'business_performance_report.csv'))
    
    pca_plot_url = url_for('static', filename='uploads/pca_plot.png')
    
    clusters = recommendations['Cluster'].unique()
    bm_cycles = recommendations['BM Cycle Name'].unique()
    
    return render_template('results.html', tables=[recommendations.to_html(classes='data'), report.to_html(classes='data')], titles=recommendations.columns.values, pca_plot_url=pca_plot_url, clusters=clusters, bm_cycles=bm_cycles)

@app.route('/filter', methods=['GET'])
def filter_results():
    cluster_filter = request.args.get('cluster')
    bm_cycle_filter = request.args.get('bm_cycle')
    
    recommendations = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'business_training_recommendations.csv'))
    
    if cluster_filter:
        recommendations = recommendations[recommendations['Cluster'] == int(cluster_filter)]
    if bm_cycle_filter:
        recommendations = recommendations[recommendations['BM Cycle Name'] == bm_cycle_filter]
    
    clusters = recommendations['Cluster'].unique()
    bm_cycles = recommendations['BM Cycle Name'].unique()
    
    return render_template('results.html', tables=[recommendations.to_html(classes='data')], titles=recommendations.columns.values, clusters=clusters, bm_cycles=bm_cycles)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
