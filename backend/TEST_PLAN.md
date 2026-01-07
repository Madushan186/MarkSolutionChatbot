# Query Parser Test Plan

## Test Categories

### 1. Quarter Queries ✓
Test that quarter queries work correctly.

**Test Cases:**
```
1. "Q1 2025"
   Expected: Show Jan, Feb, Mar 2025 with total

2. "Q1 2025 Branch 1"
   Expected: Show Q1 2025 for Branch 1

3. "First quarter 2025"
   Expected: Same as Q1 2025

4. "Quarter 2 2025"
   Expected: Show Apr, May, Jun 2025

5. "Q4 2024"
   Expected: Show Oct, Nov, Dec 2024
```

### 2. Week Queries ✓
Test week-based queries.

**Test Cases:**
```
1. "This week sales"
   Expected: Show Mon-Sun of current week

2. "Last week sales"
   Expected: Show Mon-Sun of previous week

3. "This week Branch 2"
   Expected: Show this week for Branch 2
```

### 3. Date Range Queries ✓
Test date range queries.

**Test Cases:**
```
1. "January to March 2025"
   Expected: Show Jan, Feb, Mar 2025

2. "Jan to Mar 2025"
   Expected: Same as above (short form)

3. "First half of 2025"
   Expected: Show Jan-Jun 2025

4. "Second half of 2025"
   Expected: Show Jul-Dec 2025

5. "June to August 2025 Branch 1"
   Expected: Show Jun-Aug 2025 for Branch 1
```

### 4. Existing Queries (Regression) ✓
Ensure existing queries still work.

**Test Cases:**
```
1. "Today sales"
   Expected: Today's sales for Branch 1

2. "Yesterday sales Branch 2"
   Expected: Yesterday's sales for Branch 2

3. "Past 3 months"
   Expected: Last 3 months summary

4. "June 2025 sales"
   Expected: June 2025 total

5. "2025 total"
   Expected: Year 2025 total

6. "Compare Branch 1 and Branch 2"
   Expected: Comparison table

7. "Highest performing branch this month"
   Expected: Branch with highest sales
```

### 5. Validation & Error Handling ✓
Test that validation works correctly.

**Test Cases:**
```
1. "Average sales" (no period)
   Expected: "Average of which period? Try: 'Average sales this month'..."

2. "Total sales" (no period)
   Expected: "Total sales for which period? Try: 'Today sales'..."

3. "Compare Branch 1 and Branch 2" (STAFF user)
   Expected: "Comparison queries are not available for your access level"

4. "Sales on 2026-12-31" (future date)
   Expected: "Cannot query future date: 2026-12-31"

5. "Quarter 5 2025" (invalid quarter)
   Expected: "Invalid quarter: 5. Must be 1, 2, 3, or 4"
```

### 6. Default Logic ✓
Test smart defaults.

**Test Cases:**
```
1. "Today sales" (ADMIN user, no branch specified)
   Expected: Defaults to Branch 1

2. "Today sales" (STAFF user, no branch specified)
   Expected: Defaults to user's assigned branch

3. "Past 3 months" (no branch)
   Expected: Defaults to Branch 1
```

### 7. Edge Cases ✓
Test unusual but valid queries.

**Test Cases:**
```
1. "q1 2025" (lowercase)
   Expected: Works same as "Q1 2025"

2. "QUARTER 1 2025" (uppercase)
   Expected: Works same as "Q1 2025"

3. "january-march 2025" (hyphen instead of 'to')
   Expected: Works same as "January to March 2025"

4. "first half 2025" (no 'of')
   Expected: Works same as "First half of 2025"
```

## Testing Instructions

### Manual Testing
1. Login as ADMIN user
2. Test each query from categories 1-4
3. Verify correct output format
4. Check that totals are accurate

### Role-Based Testing
1. Login as STAFF user (Branch 1)
2. Test validation cases (category 5)
3. Verify permission restrictions work

### Regression Testing
1. Test all existing queries (category 4)
2. Ensure no functionality was broken
3. Compare outputs with previous version

## Success Criteria

✅ All quarter queries return correct data
✅ All week queries return correct data
✅ All date range queries return correct data
✅ All existing queries still work (no regression)
✅ Validation catches invalid queries
✅ Error messages are helpful
✅ Defaults are applied correctly
✅ Role-based permissions work

## Known Limitations

- Growth queries not yet fully implemented (Phase 2)
- Multi-branch aggregations not yet supported
- Custom date ranges (not month-aligned) use month grouping

## Next Steps After Testing

1. Fix any bugs found
2. Add growth query handler
3. Performance optimization
4. Update documentation
