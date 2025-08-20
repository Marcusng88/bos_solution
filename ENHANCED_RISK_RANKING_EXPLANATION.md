# Enhanced Risk Ranking Logic for Overspending Predictions

## Overview

The enhanced overspending prediction system now considers multiple factors beyond just budget utilization, including net profit performance, CTR, CPC, conversion rates, and spending velocity. This provides a more comprehensive and accurate assessment of campaign risk.

## Risk Ranking Algorithm

### 1. Budget Utilization Risk (40% Weight)

**Purpose**: Primary indicator of immediate overspending risk

**Risk Levels**:
- **Critical (95%+)**: 1.0 risk score
- **High (85-95%)**: 0.8 risk score  
- **Medium (75-85%)**: 0.6 risk score
- **Low (50-75%)**: 0.3 risk score
- **Safe (<50%)**: 0.0 risk score

**Logic**: Higher budget utilization indicates greater immediate risk of overspending.

### 2. Profit Performance Risk (30% Weight)

**Purpose**: Assesses whether the campaign is generating positive returns

**Risk Levels**:
- **Severe Loss (-20%+)**: 1.0 risk score
- **Significant Loss (-10% to -20%)**: 0.8 risk score
- **Loss (0% to -10%)**: 0.6 risk score
- **Low Profit (0% to 10%)**: 0.3 risk score
- **Good Profit (10%+)**: 0.0 risk score

**Logic**: Campaigns with negative profit margins are higher risk because they're losing money while potentially overspending.

### 3. Performance Metrics Risk (20% Weight)

**Purpose**: Evaluates campaign efficiency and effectiveness

**CTR Risk**:
- **Low (<1%)**: +0.5 to performance risk
- **Below Average (1-2%)**: +0.3 to performance risk

**CPC Risk**:
- **High (>$5)**: +0.5 to performance risk
- **Above Average ($3-5)**: +0.3 to performance risk

**Conversion Rate Risk**:
- **Low (<1%)**: +0.5 to performance risk
- **Below Average (1-2%)**: +0.3 to performance risk

**Logic**: Poor performance metrics indicate inefficient spending and higher risk.

### 4. Spending Velocity Risk (10% Weight)

**Purpose**: Assesses how quickly the campaign is consuming budget

**Risk Levels**:
- **Extremely Rapid (<5 days until overspend)**: 1.0 risk score
- **Rapid (5-10 days)**: 0.8 risk score
- **Above Average (10-15 days)**: 0.5 risk score
- **Normal (>15 days)**: 0.0 risk score

**Logic**: Faster spending rates increase the urgency of intervention.

## Final Risk Level Determination

Based on the weighted risk score:

- **Critical Risk**: 0.8+ (80%+ overall risk)
- **High Risk**: 0.6-0.79 (60-79% overall risk)
- **Medium Risk**: 0.4-0.59 (40-59% overall risk)
- **Low Risk**: <0.4 (<40% overall risk)

## 📊 Example Campaigns Risk Analysis (JUST EXAMPLE ONLY)

### 1. **Maybelline New Year Glow** (ongoing: 'Yes')
- **Budget Utilization**: (6,220.11 / 38,980) × 100 = **15.9%**
- **Profit Margin**: (160.82 / 6,220.11) × 100 = **2.6%**
- **CTR**: 2.12% (Below average)
- **CPC**: $3.89 (Above average)
- **Conversion Rate**: (312 / 75,504) × 100 = **0.41%** (Low)

**Risk Calculation**:
1. Budget Risk: 0.0 × 0.4 = 0.0 (Safe)
2. Profit Risk: 0.3 × 0.3 = 0.09 (Low profit)
3. Performance Risk: (0.3 + 0.3 + 0.5) × 0.2 = 0.22 (Low CTR + High CPC + Low conversion)
4. Velocity Risk: 0.0 × 0.1 = 0.0 (Normal spending)
**Total Risk Score**: 0.31 (Low Risk - not displayed)


## 🆕 New UI Features

### Action Buttons for Risky Campaigns

Each risky campaign now displays two action buttons:

1. **Pause Campaign Button** (Red)
   - **Function**: Changes `ongoing` field from 'Yes' to 'No' in database
   - **Effect**: Completely stops the campaign
   - **Database Update**: `UPDATE campaign_data SET ongoing = 'No' WHERE name = ?`

2. **Reallocate Budget Button** (Blue)
   - **Function**: Allows users to modify the budget amount
   - **Effect**: Updates the `budget` field in database
   - **Database Update**: `UPDATE campaign_data SET budget = ? WHERE name = ?`
   - **UI**: Shows input field for new budget amount with Update/Cancel options

### Enhanced Visual Effects

- **Critical Risk**: Animated blinking red glow (`animate-pulse`)
- **High Risk**: Orange glow with orange border
- **Medium Risk**: Yellow glow with yellow border
- **Risk Score Display**: Shows percentage instead of confidence score

### Database Integration

The system now directly updates the `campaign_data` table:
- **Status Updates**: Real-time campaign pausing
- **Budget Reallocation**: Immediate budget adjustments
- **Automatic Refresh**: Predictions update after each action

## Benefits of Enhanced Logic

1. **More Accurate Risk Assessment**: Considers profitability, not just budget
2. **Better Prioritization**: High-risk campaigns with poor performance are prioritized
3. **Comprehensive View**: Shows all relevant metrics in one place
4. **Actionable Insights**: Clear risk factors guide intervention strategies
5. **Visual Clarity**: Glowing effects and color coding for quick identification
6. **Immediate Actions**: Users can pause or adjust budgets directly from the interface
7. **Real-time Updates**: Database changes reflect immediately in the UI

## Implementation Notes

- Only campaigns with medium or higher risk are displayed
- Campaigns are sorted by risk score (highest first)
- Risk scores are displayed as percentages for clarity
- All calculations are performed server-side for consistency
- Real-time data from the campaign_data table is used
- Database updates are transactional with rollback on errors
