import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

st.title("🛒 Retail Sales Analytics Dashboard")
st.write("Sales, Profit/Loss Analysis with Downloadable Reports")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload Retail Sales Dataset (CSV or Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("Dataset Loaded Successfully")
    st.dataframe(df.head())

    # ---------------- DATE PROCESSING ----------------
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month_name()

    # ---------------- FILTERS ----------------
    st.sidebar.header("📊 Filters")

    region_filter = st.sidebar.multiselect(
        "Select Region", df["Region"].unique(), df["Region"].unique()
    )

    category_filter = st.sidebar.multiselect(
        "Select Category", df["Category"].unique(), df["Category"].unique()
    )

    filtered_df = df[
        (df["Region"].isin(region_filter)) &
        (df["Category"].isin(category_filter))
    ]

    # ---------------- KPIs ----------------
    total_sales = filtered_df["Sales"].sum()
    total_profit = filtered_df["Profit"].sum()
    total_orders = filtered_df.shape[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Sales", f"₹ {total_sales:,.0f}")
    c2.metric("📈 Total Profit", f"₹ {total_profit:,.0f}")
    c3.metric("🧾 Total Orders", total_orders)

    # ---------------- MONTHLY SALES ----------------
    st.subheader("📈 Monthly Sales Trend")
    monthly_sales = filtered_df.groupby(["Year", "Month"])["Sales"].sum().reset_index()
    fig1 = px.line(monthly_sales, x="Month", y="Sales", color="Year", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- REGION SALES ----------------
    st.subheader("🌍 Sales by Region")
    region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index()
    fig2 = px.bar(region_sales, x="Region", y="Sales", text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- CATEGORY SALES ----------------
    st.subheader("🧺 Category-wise Sales")
    category_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
    fig3 = px.pie(category_sales, names="Category", values="Sales", hole=0.4)
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------- PROFIT VS LOSS ----------------
    st.subheader("📉 Profit vs Loss Analysis")
    filtered_df["Profit Status"] = filtered_df["Profit"].apply(
        lambda x: "Profit" if x > 0 else "Loss"
    )

    profit_loss = filtered_df.groupby("Profit Status")["Profit"].sum().reset_index()
    fig4 = px.bar(profit_loss, x="Profit Status", y="Profit", text_auto=True)
    st.plotly_chart(fig4, use_container_width=True)

    # ---------------- LOSS PRODUCTS ----------------
    st.subheader("🚨 Top Loss-Making Products")
    loss_products = (
        filtered_df[filtered_df["Profit"] < 0]
        .groupby("Product")["Profit"]
        .sum()
        .sort_values()
        .head(10)
        .reset_index()
    )
    st.dataframe(loss_products)

    # ---------------- DOWNLOAD EXCEL ----------------
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Filtered Data")
        region_sales.to_excel(writer, index=False, sheet_name="Region Sales")
        category_sales.to_excel(writer, index=False, sheet_name="Category Sales")
        profit_loss.to_excel(writer, index=False, sheet_name="Profit Loss")

    st.download_button(
        "📊 Download Excel Report",
        data=excel_buffer.getvalue(),
        file_name="Retail_Sales_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------------- DOWNLOAD PDF ----------------
    st.subheader("📄 Download PDF Summary Report")

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Retail Sales Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Total Sales: ₹ {total_sales:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Total Profit: ₹ {total_profit:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Total Orders: {total_orders}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Profit vs Loss Summary", styles["Heading2"]))
    table_data = [profit_loss.columns.tolist()] + profit_loss.values.tolist()
    elements.append(Table(table_data))

    doc.build(elements)

    st.download_button(
        "📄 Download PDF Report",
        data=pdf_buffer.getvalue(),
        file_name="Retail_Sales_Summary.pdf",
        mime="application/pdf"
    )

else:
    st.info("👆 Upload a dataset to start analysis.")
