import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def load_data():
    customers_df = pd.read_csv("dashboard/customers_clean_df.csv")
    order_items_df = pd.read_csv("dashboard/order_items_clean_df.csv")
    order_reviews_df = pd.read_csv("dashboard/order_reviews_clean_df.csv")
    orders_df = pd.read_csv("dashboard/orders_clean_df.csv")
    products_df = pd.read_csv("dashboard/products_clean_df.csv")

    return customers_df, order_items_df, order_reviews_df, orders_df, products_df

def main():
    st.title("Brazilian E-Commerce Public Dataset by Olist - Dashboard by Muhammad Raihan Fauzi ✨")

    customers_df, order_items_df, order_reviews_df, orders_df, products_df = load_data()

    if 'order_purchase_timestamp' in orders_df.columns:
        orders_df['order_purchase_timestamp'] = pd.to_datetime(
            orders_df['order_purchase_timestamp'], 
            errors='coerce'
        )
    else:
        st.error("Kolom 'order_purchase_timestamp' tidak ditemukan di orders_df.")
        return

    st.sidebar.image(
        "https://raw.githubusercontent.com/mraihanfauzii/Brazilian_E-Commerce_Public_Dataset/refs/heads/main/Logo-Olist.png", 
        width=200
    )
    st.sidebar.header("Filter Tanggal")
    min_date = orders_df['order_purchase_timestamp'].min()
    max_date = orders_df['order_purchase_timestamp'].max()

    start_date = st.sidebar.date_input("Start Date", value=min_date)
    end_date = st.sidebar.date_input("End Date", value=max_date)

    if start_date > end_date:
        st.sidebar.error("Tanggal awal harus lebih kecil atau sama dengan tanggal akhir.")
    
    orders_filtered = orders_df[
        (orders_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
        (orders_df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
    ].copy()

    st.write(f"**Rentang Tanggal Terpilih**: {start_date} s/d {end_date}")
    st.header("Visualisasi & RFM Analysis dengan Filter Tanggal")
    st.subheader("Kategori Produk Terbanyak & Tersedikit Terjual")
    df_merged_items_products = pd.merge(
        order_items_df,
        products_df[['product_id','product_category_name']],
        on='product_id',
        how='left'
    )
    df_merged_items_products = df_merged_items_products[
        df_merged_items_products['order_id'].isin(orders_filtered['order_id'])
    ]
    sales_by_category = df_merged_items_products.groupby('product_category_name')['order_item_id'].count().reset_index()
    sales_by_category.columns = ['product_category_name', 'total_sold']
    sales_by_category = sales_by_category.sort_values('total_sold', ascending=False)

    if len(sales_by_category) == 0:
        st.warning("Tidak ada data penjualan di rentang tanggal ini.")
    else:
        top_10 = sales_by_category.head(10)
        bottom_10 = sales_by_category.tail(10).sort_values('total_sold', ascending=True)

        fig1, ax1 = plt.subplots(figsize=(8,6))
        colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(data=top_10, y='product_category_name', x='total_sold', palette=colors, ax=ax1)
        ax1.set_title("The Most Sold Product Categories", fontsize=14, fontweight='bold')
        ax1.set_xlabel("Total Items Sold")
        ax1.set_ylabel("Product Category")
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(8,6))
        colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(data=bottom_10, y='product_category_name', x='total_sold', palette=colors, ax=ax2)
        ax2.set_title("The Least Sold Product Categories", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Total Items Sold")
        ax2.set_ylabel("Product Category")
        st.pyplot(fig2)

    st.subheader("Sebaran Pesanan (Hari & Bulan) + Pola Musiman")
    orders_filtered['year_month'] = orders_filtered['order_purchase_timestamp'].dt.to_period('M').astype(str)
    orders_filtered['day_of_week'] = orders_filtered['order_purchase_timestamp'].dt.day_name()

    orders_per_month = orders_filtered.groupby('year_month')['order_id'].count().reset_index()
    orders_per_month.columns = ['year_month','total_orders']
    fig3, ax3 = plt.subplots(figsize=(10,5))
    sns.lineplot(data=orders_per_month, x='year_month', y='total_orders', marker='o', color='#72BCD4', ax=ax3)
    ax3.set_title("Monthly Orders Over Time", fontsize=14, fontweight='bold')
    ax3.set_xlabel("Year-Month")
    ax3.set_ylabel("Total Orders")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    orders_filtered['day_of_week'] = pd.Categorical(orders_filtered['day_of_week'], categories=days_order, ordered=True)
    orders_per_day = orders_filtered.groupby('day_of_week')['order_id'].count().reset_index()

    fig4, ax4 = plt.subplots(figsize=(8,5))
    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#D3D3D3", "#D3D3D3"]
    sns.barplot(data=orders_per_day, x='day_of_week', y='order_id', palette=colors, ax=ax4)
    ax4.set_title("Orders Distribution by Day of Week", fontsize=14, fontweight='bold')
    ax4.set_xlabel("Day of Week")
    ax4.set_ylabel("Total Orders")
    st.pyplot(fig4)

    st.subheader("Performa Penjualan & Revenue (Delivered Orders)")
    delivered_filtered = orders_filtered[orders_filtered['order_status'] == 'delivered'].copy()
    orders_items_merged = pd.merge(
        delivered_filtered[['order_id','order_purchase_timestamp','order_status']],
        order_items_df[['order_id','price','freight_value']],
        on='order_id',
        how='inner'
    )
    orders_items_merged['total_revenue'] = orders_items_merged['price'] + orders_items_merged['freight_value']
    orders_items_merged['year_month'] = pd.to_datetime(orders_items_merged['order_purchase_timestamp'], errors='coerce')
    orders_items_merged['year_month'] = orders_items_merged['year_month'].dt.to_period('M').astype(str)

    monthly_perf = orders_items_merged.groupby('year_month').agg({
        'order_id': 'nunique',
        'total_revenue': 'sum'
    }).reset_index()
    monthly_perf.columns = ['year_month','total_orders','total_revenue']

    fig5, ax5 = plt.subplots(figsize=(10,5))
    sns.lineplot(data=monthly_perf, x='year_month', y='total_orders', marker='o', color='#72BCD4', ax=ax5)
    ax5.set_title("Monthly Orders (Delivered Only)", fontsize=14, fontweight='bold')
    ax5.set_xlabel("Year-Month")
    ax5.set_ylabel("Total Orders")
    plt.xticks(rotation=45)
    st.pyplot(fig5)

    fig6, ax6 = plt.subplots(figsize=(10,5))
    sns.lineplot(data=monthly_perf, x='year_month', y='total_revenue', marker='o', color='#72BCD4', ax=ax6)
    ax6.set_title("Monthly Revenue (Delivered Only)", fontsize=14, fontweight='bold')
    ax6.set_xlabel("Year-Month")
    ax6.set_ylabel("Total Revenue")
    plt.xticks(rotation=45)
    st.pyplot(fig6)

    st.subheader("Perbandingan Rating Tinggi (3-5) vs Rendah (1-2)")
    order_reviews_merged = pd.merge(
        order_reviews_df,
        orders_filtered[['order_id','order_status']],
        on='order_id',
        how='left'
    )
    order_reviews_merged = order_reviews_merged[order_reviews_merged['order_status'] == 'delivered']
    order_reviews_merged['rating_label'] = order_reviews_merged['review_score'].apply(
        lambda x: 'High (3-5)' if x >= 3 else 'Low (1-2)'
    )
    rating_counts = order_reviews_merged['rating_label'].value_counts().reset_index()
    rating_counts.columns = ['rating_label','count']

    col1, col2 = st.columns(2)
    with col1:
        fig7, ax7 = plt.subplots(figsize=(5,4))
        colors = ["#72BCD4", "#D3D3D3"]
        sns.barplot(data=rating_counts, x='rating_label', y='count', palette=colors, ax=ax7)
        ax7.set_title("Bar: High vs. Low Ratings", fontsize=12, fontweight='bold')
        ax7.set_xlabel("Rating Category")
        ax7.set_ylabel("Number of Orders")
        st.pyplot(fig7)

    with col2:
        fig8, ax8 = plt.subplots(figsize=(5,3))
        ax8.pie(
            rating_counts['count'],
            labels=rating_counts['rating_label'],
            autopct='%1.1f%%',
            startangle=140,
            colors=["#72BCD4", "#D3D3D3"]
        )
        ax8.set_title("Pie: High vs. Low Ratings", fontsize=12, fontweight='bold')
        ax8.axis('equal')
        st.pyplot(fig8)

    st.subheader("Retensi Pelanggan (Customer Retention) vs. Churn Rate")
    df_customer_orders = pd.merge(
        orders_filtered[['order_id','customer_id','order_status']],
        customers_df[['customer_id','customer_unique_id']],
        on='customer_id',
        how='left'
    )
    df_customer_orders = df_customer_orders[df_customer_orders['order_status'] == 'delivered']
    customer_order_counts = df_customer_orders.groupby('customer_unique_id')['order_id'].nunique().reset_index(name='total_orders')

    customer_order_counts['retention_label'] = customer_order_counts['total_orders'].apply(
        lambda x: 'One-time' if x == 1 else 'Repeat'
    )
    retention_counts = customer_order_counts['retention_label'].value_counts().reset_index()
    retention_counts.columns = ['retention_label','count']

    col3, col4 = st.columns(2)
    with col3:
        fig9, ax9 = plt.subplots(figsize=(5,4))
        colors = ["#72BCD4", "#D3D3D3"]
        sns.barplot(data=retention_counts, x='retention_label', y='count', palette=colors, ax=ax9)
        ax9.set_title("Bar: Retention vs. Churn", fontsize=12, fontweight='bold')
        ax9.set_xlabel("Customer Type")
        ax9.set_ylabel("Number of Customers")
        st.pyplot(fig9)

    with col4:
        fig10, ax10 = plt.subplots(figsize=(5,3))
        ax10.pie(
            retention_counts['count'],
            labels=retention_counts['retention_label'],
            autopct='%1.1f%%',
            startangle=140,
            colors = ["#72BCD4", "#D3D3D3"]
        )
        ax10.set_title("Pie: Retention vs. Churn", fontsize=12, fontweight='bold')
        ax10.axis('equal')
        st.pyplot(fig10)

    df_orders_delivered = orders_filtered[orders_filtered['order_status'] == 'delivered'].copy()
    df_merged = pd.merge(
        df_orders_delivered[['order_id','customer_id','order_purchase_timestamp']],
        order_items_df[['order_id','price','freight_value']],
        on='order_id',
        how='inner'
    )
    df_merged = pd.merge(
        df_merged,
        customers_df[['customer_id','customer_unique_id']],
        on='customer_id',
        how='left'
    )
    df_merged['total_revenue'] = df_merged['price'] + df_merged['freight_value']

    if df_merged['order_purchase_timestamp'].notnull().sum() > 0:
        max_timestamp = df_merged['order_purchase_timestamp'].max()
        snapshot_date = pd.to_datetime(max_timestamp) + pd.Timedelta(days=1)
    else:
        snapshot_date = pd.to_datetime('1900-01-01')

    rfm_df = df_merged.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique',
        'total_revenue': 'sum'
    }).reset_index()

    rfm_df.columns = ['customer_unique_id','last_purchase_date','frequency','monetary']
    rfm_df['recency'] = (pd.to_datetime(snapshot_date) - pd.to_datetime(rfm_df['last_purchase_date'])).dt.days

    def rfm_score_rank(data, col, ascending=True):
        ranked = data[col].rank(method='first', ascending=ascending)
        if ascending:
            return pd.qcut(ranked, 5, labels=[5,4,3,2,1])
        else:
            return pd.qcut(ranked, 5, labels=[1,2,3,4,5])

    if len(rfm_df) > 0:
        rfm_df['R_score'] = rfm_score_rank(rfm_df, 'recency', ascending=True).astype(int)
        rfm_df['F_score'] = rfm_score_rank(rfm_df, 'frequency', ascending=False).astype(int)
        rfm_df['M_score'] = rfm_score_rank(rfm_df, 'monetary', ascending=False).astype(int)

        def rfm_segment(row):
            total_score = row['R_score'] + row['F_score'] + row['M_score']
            if total_score >= 13:
                return 'Best Customers'
            elif total_score >= 10:
                return 'Loyal Customers'
            elif total_score >= 7:
                return 'Potential Loyalist'
            elif total_score >= 5:
                return 'At Risk'
            else:
                return 'Churned / Low Value'

        rfm_df['Segment'] = rfm_df.apply(rfm_segment, axis=1)
        rfm_segments = rfm_df['Segment'].value_counts().reset_index()
        rfm_segments.columns = ['Segment','Count']

        st.subheader("Distribusi Segmen RFM")
        fig_rfm, ax_rfm = plt.subplots(figsize=(7,5))
        colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
        sns.barplot(data=rfm_segments, x='Segment', y='Count', palette=colors, ax=ax_rfm)
        ax_rfm.set_title("RFM Segments Distribution", fontsize=14, fontweight='bold')
        ax_rfm.set_xlabel("Segment")
        ax_rfm.set_ylabel("Number of Customers")
        plt.xticks(rotation=30)
        st.pyplot(fig_rfm)
    else:
        st.warning("Data RFM tidak tersedia untuk rentang tanggal ini (tidak ada transaksi).")

if __name__ == "__main__":
    main()
