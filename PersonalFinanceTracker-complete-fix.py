import streamlit as st
import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    page_title="Interactive Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# --- Data & State Management ---
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None

# --- Category Lists ---
income_categories = ['Salary', 'Business/Profession', 'Interest', 'Dividends', 'Capital Gains', 'Rental', 'Other Asset Income', 'Refunds/Reimbursements', 'Gifts', 'Transfers In', 'Other/One time']
expense_categories = ['Rent', 'Home Loan', 'Vehicle loan', 'Transport', 'Outside Food', 'Groceries', 'Utilities', 'Insurance', 'Health', 'Family & Education', 'Lifestyle', 'Travel', 'Fuel', 'Taxes', 'Savings & Investments', 'House help & Services', 'One-time', 'Transfers Out', 'Other/One time']

# --- Dashboard Plotting Function ---
def plot_dashboard():
    income_by_cat, expense_by_cat = {}, {}
    for t in st.session_state.transactions:
        cats = income_by_cat if t["type"] == "income" else expense_by_cat
        cats[t["category"]] = cats.get(t["category"], 0) + t["amount"]
    
    total_income = sum(income_by_cat.values())
    total_expense = sum(expense_by_cat.values())
    balance = total_income - total_expense
    
    # Create figure with explicit backend
    fig, axs = plt.subplots(1, 3, figsize=(20, 6))
    
    # Chart 1: Income
    if total_income > 0:
        axs[0].pie(income_by_cat.values(), labels=income_by_cat.keys(), autopct='%1.1f%%', startangle=90)
        axs[0].set_title('Income Sources', fontsize=14)
    else:
        axs[0].text(0.5, 0.5, 'No Income Data', ha='center', va='center')
        axs[0].axis('off')
    
    # Chart 2: Expense
    if total_expense > 0:
        axs[1].pie(expense_by_cat.values(), labels=expense_by_cat.keys(), autopct='%1.1f%%', startangle=90)
        axs[1].set_title('Expense Categories', fontsize=14)
    else:
        axs[1].text(0.5, 0.5, 'No Expense Data', ha='center', va='center')
        axs[1].axis('off')
    
    # Chart 3: Allocation
    if total_income > 0:
        savings = max(0, balance)
        display_expense = min(total_expense, total_income)
        if display_expense > 0 or savings > 0:
            axs[2].pie([display_expense, savings], 
                      labels=[f'Expenses (${display_expense:,.2f})', f'Savings (${savings:,.2f})'], 
                      autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
            axs[2].set_title('Income Allocation', fontsize=14)
        else:
            axs[2].text(0.5, 0.5, 'No Income Data', ha='center', va='center')
            axs[2].axis('off')
    else:
        axs[2].text(0.5, 0.5, 'No Income Data', ha='center', va='center')
        axs[2].axis('off')
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)  # Close figure to prevent memory issues
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Income", f"${total_income:,.2f}")
    col2.metric("💸 Total Expense", f"${total_expense:,.2f}")
    col3.metric("🏦 Current Balance", f"${balance:,.2f}")

# --- App Layout ---
st.title("📊 Interactive Finance Tracker")
st.markdown("Log your income and expenses below to see your financial dashboard update in real-time.")

# --- Input Form ---
st.header("Add or Edit Transaction")

col1, col2 = st.columns([1, 2])

with col1:
    if st.session_state.editing_index is not None:
        transaction = st.session_state.transactions[st.session_state.editing_index]
        default_type_index = 0 if transaction['type'] == 'income' else 1
        default_cat_list = income_categories if transaction['type'] == 'income' else expense_categories
        default_cat_index = default_cat_list.index(transaction['category'])
        default_amount = transaction['amount']
    else:
        default_type_index, default_cat_index, default_amount = 0, 0, 0.0
    
    trans_type = st.selectbox("Type:", ["Income", "Expense"], index=default_type_index)
    categories = income_categories if trans_type == "Income" else expense_categories
    trans_category = st.selectbox("Category:", categories, index=default_cat_index)
    trans_amount = st.number_input("Amount:", min_value=0.01, value=default_amount, format="%.2f")
    
    if st.button("💾 Save Transaction"):
        new_transaction = {"type": trans_type.lower(), "category": trans_category, "amount": trans_amount}
        
        if st.session_state.editing_index is not None:
            st.session_state.transactions[st.session_state.editing_index] = new_transaction
            st.success("Transaction updated successfully!")
            st.session_state.editing_index = None
        else:
            st.session_state.transactions.append(new_transaction)
            st.success("Transaction added successfully!")
        
        st.rerun()

# --- Dashboard Display ---
st.header("📈 Your Financial Dashboard")

if not st.session_state.transactions:
    st.info("Dashboard will appear here once you add a transaction.")
else:
    plot_dashboard()

# --- Transaction Management ---
st.header("Manage Transactions")

if not st.session_state.transactions:
    st.info("Your transactions will be listed here.")
else:
    for i, t in enumerate(st.session_state.transactions):
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
        
        with col1:
            st.write(f"**#{i+1}**")
        with col2:
            st.write(t['type'].title())
        with col3:
            st.write(f"${t['amount']:,.2f} ({t['category']})")
        with col4:
            if st.button("✏️ Edit", key=f"edit_{i}"):
                st.session_state.editing_index = i
                st.rerun()
        with col5:
            if st.button("🗑️ Delete", key=f"delete_{i}"):
                st.session_state.transactions.pop(i)
                st.rerun()