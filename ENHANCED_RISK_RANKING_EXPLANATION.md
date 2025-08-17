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

## 📊 Complete Ongoing Campaigns Risk Analysis

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

### 2. **HP Spectre X360** (ongoing: 'Yes') ⚠️ **CRITICAL RISK**
- **Budget Utilization**: (8,582 / 8,903) × 100 = **96.4%**
- **Profit Margin**: (-2,347.18 / 8,582) × 100 = **-27.4%**
- **CTR**: 2.53% (Below average)
- **CPC**: $1.57 (Good)
- **Conversion Rate**: (245 / 551,551) × 100 = **0.04%** (Very low)

**Risk Calculation**:
1. Budget Risk: 1.0 × 0.4 = 0.4 (Critical)
2. Profit Risk: 1.0 × 0.3 = 0.3 (Severe loss)
3. Performance Risk: (0.3 + 0.0 + 0.5) × 0.2 = 0.16 (Low CTR + Good CPC + Very low conversion)
4. Velocity Risk: 1.0 × 0.1 = 0.1 (Extremely rapid)
**Total Risk Score**: 0.96 (Critical Risk)

### 3. **Guinness Black Party** (ongoing: 'Yes')
- **Budget Utilization**: (19,775.28 / 43,954) × 100 = **45.0%**
- **Profit Margin**: (7,013.75 / 19,775.28) × 100 = **35.4%**
- **CTR**: 4.86% (Good)
- **CPC**: $2.98 (Good)
- **Conversion Rate**: (1,107 / 136,670) × 100 = **0.81%** (Low)

**Risk Calculation**:
1. Budget Risk: 0.0 × 0.4 = 0.0 (Safe)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Good profit)
3. Performance Risk: (0.0 + 0.0 + 0.3) × 0.2 = 0.06 (Good CTR + Good CPC + Low conversion)
4. Velocity Risk: 0.0 × 0.1 = 0.0 (Normal spending)
**Total Risk Score**: 0.06 (Low Risk - not displayed)

### 4. **Uniqlo TechWear 2025** (ongoing: 'Yes')
- **Budget Utilization**: (12,417.49 / 41,724) × 100 = **29.8%**
- **Profit Margin**: (3,074.51 / 12,417.49) × 100 = **24.8%**
- **CTR**: 1.18% (Below average)
- **CPC**: $1.31 (Good)
- **Conversion Rate**: (1,033 / 803,002) × 100 = **0.13%** (Very low)

**Risk Calculation**:
1. Budget Risk: 0.0 × 0.4 = 0.0 (Safe)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Good profit)
3. Performance Risk: (0.3 + 0.0 + 0.5) × 0.2 = 0.16 (Low CTR + Good CPC + Very low conversion)
4. Velocity Risk: 0.0 × 0.1 = 0.0 (Normal spending)
**Total Risk Score**: 0.16 (Low Risk - not displayed)

### 5. **IKEA Home Living** (ongoing: 'Yes') ⚠️ **MEDIUM RISK**
- **Budget Utilization**: (3,531 / 3,760) × 100 = **93.9%**
- **Profit Margin**: (1,127.82 / 3,531) × 100 = **31.9%**
- **CTR**: 1.53% (Below average)
- **CPC**: $2.62 (Good)
- **Conversion Rate**: (104 / 207,233) × 100 = **0.05%** (Very low)

**Risk Calculation**:
1. Budget Risk: 0.8 × 0.4 = 0.32 (High)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Good profit)
3. Performance Risk: (0.3 + 0.0 + 0.5) × 0.2 = 0.16 (Low CTR + Good CPC + Very low conversion)
4. Velocity Risk: 0.8 × 0.1 = 0.08 (Rapid)
**Total Risk Score**: 0.56 (Medium Risk)

### 6. **Harvey Norman Big Sale** (ongoing: 'Yes')
- **Budget Utilization**: (18,754 / 23,891) × 100 = **78.5%**
- **Profit Margin**: (8,085.92 / 18,754) × 100 = **43.1%**
- **CTR**: 5.86% (Good)
- **CPC**: $1.95 (Good)
- **Conversion Rate**: (8,094 / 800,016) × 100 = **1.01%** (Below average)

**Risk Calculation**:
1. Budget Risk: 0.6 × 0.4 = 0.24 (Above 75%)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Good profit)
3. Performance Risk: (0.0 + 0.0 + 0.3) × 0.2 = 0.06 (Good CTR + Good CPC + Below average conversion)
4. Velocity Risk: 0.5 × 0.1 = 0.05 (Above average)
**Total Risk Score**: 0.35 (Low Risk - not displayed)

### 7. **Sony Bravia OLED Launch** (ongoing: 'Yes')
- **Budget Utilization**: (2,130.24 / 25,750) × 100 = **8.3%**
- **Profit Margin**: (987.79 / 2,130.24) × 100 = **46.4%**
- **CTR**: 5.59% (Good)
- **CPC**: $0.48 (Excellent)
- **Conversion Rate**: (774 / 79,438) × 100 = **0.97%** (Below average)

**Risk Calculation**:
1. Budget Risk: 0.0 × 0.4 = 0.0 (Safe)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Good profit)
3. Performance Risk: (0.0 + 0.0 + 0.3) × 0.2 = 0.06 (Good CTR + Excellent CPC + Below average conversion)
4. Velocity Risk: 0.0 × 0.1 = 0.0 (Normal spending)
**Total Risk Score**: 0.06 (Low Risk - not displayed)

### 8. **Panasonic Eco Home** (ongoing: 'Yes')
- **Budget Utilization**: (763.73 / 46,552) × 100 = **1.6%**
- **Profit Margin**: (276.73 / 763.73) × 100 = **36.2%**
- **CTR**: 0.77% (Low)
- **CPC**: $0.53 (Excellent)
- **Conversion Rate**: (125 / 188,202) × 100 = **0.07%** (Very low)

**Risk Calculation**:
1. Budget Risk: 0.0 × 0.4 = 0.0 (Safe)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Good profit)
3. Performance Risk: (0.5 + 0.0 + 0.5) × 0.2 = 0.2 (Low CTR + Excellent CPC + Very low conversion)
4. Velocity Risk: 0.0 × 0.1 = 0.0 (Normal spending)
**Total Risk Score**: 0.2 (Low Risk - not displayed)

### 9. **Shopee Raya 2025** (ongoing: 'Yes')
- **Budget Utilization**: (15,423 / 30,181) × 100 = **51.1%**
- **Profit Margin**: (3,664.87 / 15,423) × 100 = **23.8%**
- **CTR**: 5.49% (Good)
- **CPC**: $2.01 (Good)
- **Conversion Rate**: (759 / 103,525) × 100 = **0.73%** (Low)

**Risk Calculation**:
1. Budget Risk: 0.3 × 0.4 = 0.12 (Moderate)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Good profit)
3. Performance Risk: (0.0 + 0.0 + 0.3) × 0.2 = 0.06 (Good CTR + Good CPC + Low conversion)
4. Velocity Risk: 0.0 × 0.1 = 0.0 (Normal spending)
**Total Risk Score**: 0.18 (Low Risk - not displayed)

### 10. **Lazada Flash Sales 8.8** (ongoing: 'Yes')
- **Budget Utilization**: (12,645 / 32,654) × 100 = **38.7%**
- **Profit Margin**: (9,874 / 12,645) × 100 = **78.1%**
- **CTR**: 3.54% (Good)
- **CPC**: $4.25 (Above average)
- **Conversion Rate**: (4,656 / 325,749) × 100 = **1.43%** (Below average)

**Risk Calculation**:
1. Budget Risk: 0.0 × 0.4 = 0.0 (Safe)
2. Profit Risk: 0.0 × 0.3 = 0.0 (Excellent profit)
3. Performance Risk: (0.0 + 0.3 + 0.3) × 0.2 = 0.12 (Good CTR + Above average CPC + Below average conversion)
4. Velocity Risk: 0.0 × 0.1 = 0.0 (Normal spending)
**Total Risk Score**: 0.12 (Low Risk - not displayed)

## 🎯 Risk Level Summary

**Critical Risk (0.8+)**: 1 campaign
- HP Spectre X360: 0.96 (96%)

**High Risk (0.6-0.79)**: 0 campaigns

**Medium Risk (0.4-0.59)**: 1 campaign  
- IKEA Home Living: 0.56 (56%)

**Low Risk (<0.4)**: 8 campaigns (not displayed in predictions)

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
