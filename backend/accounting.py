import sqlite3
import datetime

DB_NAME = "sales.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def get_hierarchy_tree(root_id=None):
    """
    Fetches the CoA hierarchy differently based on usage.
    If root_id is provided, returns subtree.
    Otherwise returns full tree structure.
    Output compatible with ASCII formatter.
    """
    conn = get_db()
    cur = conn.cursor()
    
    # Recursive CTE to get hierarchy in order
    query = """
    WITH RECURSIVE coa_tree AS (
        SELECT id, parent_id, name, level, type, allow_ledger, 0 as depth, cast(id as text) as path
        FROM accounts
        WHERE parent_id IS NULL -- Roots
        UNION ALL
        SELECT a.id, a.parent_id, a.name, a.level, a.type, a.allow_ledger, ct.depth + 1, ct.path || '/' || a.id
        FROM accounts a
        JOIN coa_tree ct ON a.parent_id = ct.id
    )
    SELECT id, parent_id, name, level, type, allow_ledger, depth FROM coa_tree ORDER BY path;
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    
    return rows # List of tuples

def get_account_balance(account_name, target_year=None, br_id="ALL"):
    """
    Returns the aggregated balance for a given account name.
    """
    conn = get_db()
    cur = conn.cursor()
    
    # 1. Find Account Info
    cur.execute("SELECT id, allow_ledger FROM accounts WHERE name LIKE ? LIMIT 1", (account_name,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None, "Account Not Found"
    
    acc_id, allow_ledger = row
    
    if not target_year:
        target_year = datetime.datetime.now().year

    # Branch Filter Logic
    br_filter = ""
    params = []
    if br_id != "ALL":
        br_filter = "AND br_id = ?"
        params.append(br_id)

    # 2. Aggregation Logic
    if allow_ledger == 'yes':
        query = f"SELECT SUM(amount) FROM sales WHERE account_id = ? AND strftime('%Y', sale_date) = ? {br_filter}"
        # Params: account_id, year, [br_id]
        cur.execute(query, (acc_id, str(target_year), *params))
        val = cur.fetchone()[0]
        total = float(val) if val else 0.0
    else:
        # Group: Find all descendants
        leaf_query = f"""
        WITH RECURSIVE descendants AS (
            SELECT id, allow_ledger FROM accounts WHERE id = ?
            UNION ALL
            SELECT a.id, a.allow_ledger FROM accounts a JOIN descendants d ON a.parent_id = d.id
        )
        SELECT SUM(s.amount) 
        FROM sales s
        JOIN descendants d ON s.account_id = d.id
        WHERE d.allow_ledger = 'yes'
        AND strftime('%Y', s.sale_date) = ?
        {br_filter}
        """
        # Params: acc_id, year, [br_id]
        cur.execute(leaf_query, (acc_id, str(target_year), *params))
        val = cur.fetchone()[0]
        total = float(val) if val else 0.0

    conn.close()
    return total, "OK"
