// js/assessment/scoring_assessment.js
// Handles SDG score calculation logic

function calculateAllSdgScores(data) {
    const scores = [];
    const maxScorePerSdg = 10; // Target max score

    for (let i = 1; i <= TOTAL_SDGS; i++) {
        const sdgId = `sdg-${i}`;
        const sdgInputData = data[sdgId] || { inputs: {}, notes: '' }; // Get data or default
        let directScore = 0;
        let bonusScore = 0;

        // --- Scoring Logic per SDG ---
        if (sdgId === 'sdg-1') {
            const costReductionValue = sdgInputData.inputs['sdg1_cost_reduction'];
            switch (costReductionValue) {
                case 'cost_reduc_2': directScore = 3; break;      // Basic reduction
                case 'cost_reduc_3': directScore = 5; break;      // Moderate reduction
                case 'cost_reduc_4': directScore = 7; break;      // Significant reduction
                case 'self_sufficient': directScore = 9; break;   // Self-sufficient (no cost)
                case 'energy_producing': directScore = 10; break; // Energy producing (max score)
                default: directScore = 0; break;                  // Other / Not selected
            }
            // TODO: Add scoring for other SDG 1 questions when provided

        } else if (sdgId === 'sdg-2') {
            const foodIntegrationValue = sdgInputData.inputs['sdg2_food_integration'];
            switch (foodIntegrationValue) {
                case 'none': directScore = 0; break;         // No change - baseline
                case 'study': directScore = 2; break;        // Basic planning (was 1)
                case 'conversion': directScore = 4; break;   // Future potential (was 1.5)
                case 'community': directScore = 6; break;    // Community impact (was 3)
                case 'private': directScore = 8; break;      // Individual impact (was 4)
                case 'production': directScore = 10; break;  // Maximum impact (was 6)
                default: directScore = 0; break;             // Includes 'other'
            }
             // TODO: Add scoring for other SDG 2 questions when provided

        } else if (sdgId === 'sdg-3') {
            const healthSummaryValue = sdgInputData.inputs['sdg3_health_summary'];
            switch (healthSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 2; break;  // 1 point respected
                case '2': directScore = 4; break;  // 2 points respected
                case '3': directScore = 6; break;  // 3 points respected
                case '4': directScore = 8; break;  // 4 points respected
                case '5': directScore = 10; break; // All (5+) respected (max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: If all checkboxes are ticked AND 'All' is selected
            const actionsChecked = sdgInputData.inputs['sdg3_actions'] || [];
            if (healthSummaryValue === '5' && actionsChecked.length >= 6) {
                bonusScore = 1; // Add a bonus point for confirming all specifics
            }

        } else if (sdgId === 'sdg-4') {
            // Score based on the accessibility summary radio button
            const accessSummaryValue = sdgInputData.inputs['sdg4_accessibility_summary'];
            switch (accessSummaryValue) {
                case '0': directScore = 0; break;     // None
                case 'study': directScore = 2; break; // Studies only (increased from 1)
                case '1': directScore = 3; break;     // 1 aspect included (increased from 2)
                case '2': directScore = 5; break;     // 2 aspects included (increased from 4)
                case '3': directScore = 7; break;     // 3 aspects included (increased from 6)
                case '4': directScore = 10; break;    // All 4 aspects included (increased from 8)
                default: directScore = 0; break;      // Other / Not selected
            }

        } else if (sdgId === 'sdg-5') {
             // Score based on the gender equality summary radio button
            const equalitySummaryValue = sdgInputData.inputs['sdg5_equality_summary'];
             switch (equalitySummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 2; break;  // 1 point respected
                case '2': directScore = 4; break;  // 2 points respected
                case '3': directScore = 6; break;  // 3 points respected
                case '4': directScore = 8; break;  // 4 points respected
                case '5': directScore = 10; break; // All 5 respected (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
             // Optional Bonus:
             const actionsChecked = sdgInputData.inputs['sdg5_actions'] || [];
             if (equalitySummaryValue === '5' && actionsChecked.length >= 5) {
                 bonusScore = 1;
             }

        } else if (sdgId === 'sdg-6') {
            // Score based on the water management summary radio button
            const waterSummaryValue = sdgInputData.inputs['sdg6_water_summary'];
            switch (waterSummaryValue) {
                case '0': directScore = 0; break;   // None
                case '1': directScore = 1.5; break; // 1 point respected
                case '2': directScore = 3; break;   // 2 points respected
                case '3': directScore = 5; break;   // 3 points respected
                case '4': directScore = 7; break;   // 4 points respected
                case '5': directScore = 8.5; break; // All 5 points respected
                case 'exceptional': directScore = 10; break; // Max points for exceptional measures
                default: directScore = 0; break;     // Other / Not selected
            }

        } else if (sdgId === 'sdg-7') {
             // Score based on the renewable energy impact radio button
            const renewableImpactValue = sdgInputData.inputs['sdg7_renewable_impact'];
            switch (renewableImpactValue) {
                case 'none': directScore = 0; break;
                case 'reduc_25': directScore = 2; break;
                case 'reduc_50': directScore = 4; break;
                case 'reduc_75': directScore = 6; break;
                case 'neutral': directScore = 8; break;
                case 'positive': directScore = 10; break; // Max score for positive energy
                default: directScore = 0; break;     // Other / Not selected
            }
        } else if (sdgId === 'sdg-8') {
            let score_social = 0;
            let score_technical = 0;

            // Score Part 1: Social Summary (Max 5 points for this part)
            const socialSummaryValue = sdgInputData.inputs['sdg8_social_summary'];
            switch (socialSummaryValue) {
                case '0': score_social = 0; break;    // None
                case '1': score_social = 1; break;    // 1 point
                case '2': score_social = 2; break;    // 2 points
                case '3': score_social = 3; break;    // 3 points
                case '4': score_social = 4; break;    // 4 points
                case '5': score_social = 5; break;    // All 5 social points respected
                default: score_social = 0; break;
            }

            // Score Part 2: Technical Summary (Max 5 points for this part)
            const technicalSummaryValue = sdgInputData.inputs['sdg8_technical_summary'];
            switch (technicalSummaryValue) {
                case '0': score_technical = 0; break; // None
                case '1': score_technical = 1; break; // 1 point
                case '2': score_technical = 2; break; // 2 points
                case '3': score_technical = 3; break; // 3 points
                case '4': score_technical = 4; break; // 4 points
                case '5': score_technical = 5; break; // All 5 technical points respected
                default: score_technical = 0; break;
            }

            // Combine scores (direct sum since each part is properly scaled 0-5)
            directScore = score_social + score_technical;
            // No bonus defined yet for SDG 8
        } else if (sdgId === 'sdg-9') {
            // Score based on the innovation/infrastructure summary radio button
            const innovationSummaryValue = sdgInputData.inputs['sdg9_innovation_summary'];
            switch (innovationSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 2; break;  // 1 aspect addressed
                case '2': directScore = 4; break;  // 2 aspects addressed
                case '3': directScore = 6; break;  // 3 aspects addressed
                case '4': directScore = 8; break;  // 4 aspects addressed
                case '5': directScore = 10; break; // All 5 aspects addressed (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg9_checks'] || [];
            // if (innovationSummaryValue === '5' && (checks.includes('innovate_process') || checks.includes('renovation')) ) {
            //    bonusScore = 1; // Example: Bonus for specific high-impact items within the 'all' category
            // }
        } else if (sdgId === 'sdg-10') {
            // Score based on the inclusion summary radio button
            const inclusionSummaryValue = sdgInputData.inputs['sdg10_inclusion_summary'];
            switch (inclusionSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 2; break;  // 1 aspect respected
                case '2': directScore = 4; break;  // 2 aspects respected
                case '3': directScore = 6; break;  // 3 aspects respected
                case '4': directScore = 8; break;  // 4 aspects respected
                case '5': directScore = 10; break; // All 5 aspects respected (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg10_checks'] || [];
            // if(inclusionSummaryValue === '5' && checks.length >= 5) {
            //     bonusScore = 1; // Small bonus for explicitly ticking all details
            // }
        } else if (sdgId === 'sdg-11') {
            // Score based on the sustainability summary radio button
            const sustainabilitySummaryValue = sdgInputData.inputs['sdg11_measures'];
            switch (sustainabilitySummaryValue) {
                case 'none': directScore = 0; break;   // None
                case 'one': directScore = 2; break;    // 1 aspect respected
                case 'two': directScore = 4; break;    // 2 aspects respected
                case 'three': directScore = 6; break;  // 3 aspects respected
                case 'four': directScore = 8; break;   // 4 aspects respected
                case 'five': directScore = 10; break;  // All 5 aspects respected (Max score)
                default: directScore = 0; break;       // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg11_checks'] || [];
            // if(sustainabilitySummaryValue === 'five' && checks.length >= 5) {
            //    bonusScore = 1; // Example: Small bonus for confirming all details
            // }
        } else if (sdgId === 'sdg-12') {
            // Score based on the consumption/production summary radio button
            const consumptionSummaryValue = sdgInputData.inputs['sdg12_consumption_summary'];
            switch (consumptionSummaryValue) {
                case '0': directScore = 0; break;   // None
                case '1': directScore = 2; break;   // 1 aspect respected
                case '2': directScore = 4; break;   // 2 aspects respected
                case '3': directScore = 6; break;   // 3 aspects respected
                case '4': directScore = 7; break;   // 4 aspects respected
                case '5': directScore = 8.5; break; // 5 aspects respected
                case '6': directScore = 10; break;  // All 6 aspects respected (Max score)
                default: directScore = 0; break;    // Other / Not selected
            }
             // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
             // const checks = sdgInputData.inputs['sdg12_checks'] || [];
             // if(consumptionSummaryValue === '6' && checks.length >= 6) {
             //    bonusScore = 1; // Example: Small bonus for confirming all details
             // }
        } else if (sdgId === 'sdg-13') {
            let score_actions = 0;
            let score_carbon = 0;

            // Score Part 1: Environmental Actions Summary (Max 5 points)
            const actionsSummaryValue = sdgInputData.inputs['sdg13_actions_summary'];
            switch (actionsSummaryValue) {
                case '0': score_actions = 0; break;   // None
                case '1': score_actions = 1; break;   // 1 action implemented
                case '2': score_actions = 2; break;   // 2 actions implemented
                case '3': score_actions = 3; break;   // 3 actions implemented
                case '4': score_actions = 4; break;   // 4 actions implemented
                case '5': score_actions = 5; break;   // All 5 actions implemented
                default: score_actions = 0; break;
            }

            // Score Part 2: Carbon Reduction Impact (Max 5 points)
            const carbonReductionValue = sdgInputData.inputs['sdg13_carbon_reduction'];
            switch (carbonReductionValue) {
                case 'none': score_carbon = 0; break;      // No reduction
                case 'minimal': score_carbon = 1; break;   // <25% reduction
                case 'moderate': score_carbon = 2; break;  // 25-50% reduction
                case 'significant': score_carbon = 3; break; // 50-75% reduction
                case 'major': score_carbon = 4; break;     // 75-100% reduction
                case 'negative': score_carbon = 5; break;  // Carbon negative
                default: score_carbon = 0; break;
            }

            // Combine scores (direct sum since each part is properly scaled 0-5)
            directScore = score_actions + score_carbon;
            // Optional Bonus: Could add bonus for specific checks if needed
        } else if (sdgId === 'sdg-14') {
            // Score based on the marine pollution summary radio button
            const pollutionSummaryValue = sdgInputData.inputs['sdg14_pollution_summary'];
            switch (pollutionSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 2; break;  // 1 aspect respected
                case '2': directScore = 4; break;  // 2 aspects respected
                case '3': directScore = 6; break;  // 3 aspects respected
                case '4': directScore = 8; break;  // 4 aspects respected
                case '5': directScore = 10; break; // All 5 aspects respected (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg14_checks'] || [];
            // if(pollutionSummaryValue === '5' && checks.length >= 5) {
            //    bonusScore = 1; // Example: Small bonus for confirming all details
            // }
        } else if (sdgId === 'sdg-15') {
            let score_ecosystem = 0;
            let score_artificialisation = 0;

            // Score Part 1: Ecosystem Actions Summary (Max 5 points)
            const ecosystemSummaryValue = sdgInputData.inputs['sdg15_ecosystem_summary'];
            switch (ecosystemSummaryValue) {
                case '0': score_ecosystem = 0; break;    // None
                case '1': score_ecosystem = 1; break;    // 1 action implemented
                case '2': score_ecosystem = 2; break;    // 2 actions implemented
                case '3': score_ecosystem = 3; break;    // 3 actions implemented
                case '4': score_ecosystem = 4; break;    // 4 actions implemented
                case '5': score_ecosystem = 5; break;    // All 5 actions implemented
                default: score_ecosystem = 0; break;
            }

            // Score Part 2: Land Artificialisation Ratio (Max 5 points)
            const artificialisationRatio = sdgInputData.inputs['sdg15_artificialisation_ratio'];
            switch (artificialisationRatio) {
                case '100': score_artificialisation = 0; break; // 100% artificial
                case '80': score_artificialisation = 1; break;  // 80% artificial
                case '60': score_artificialisation = 2; break;  // 60% artificial
                case '40': score_artificialisation = 3; break;  // 40% artificial
                case '20': score_artificialisation = 4; break;  // 20% artificial
                case '0': score_artificialisation = 5; break;   // 0% artificial (full renaturation)
                default: score_artificialisation = 0; break;
            }

            // Combine scores (direct sum since each part is properly scaled 0-5)
            directScore = score_ecosystem + score_artificialisation;
            // Optional Bonus: Could add bonus for specific checks if needed
        } else if (sdgId === 'sdg-16') {
            // Score based on the peace/justice/institutions summary radio button
            const peaceSummaryValue = sdgInputData.inputs['sdg16_peace_summary'];
            switch (peaceSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 2; break;  // 1 aspect respected
                case '2': directScore = 4; break;  // 2 aspects respected
                case '3': directScore = 6; break;  // 3 aspects respected
                case '4': directScore = 8; break;  // 4 aspects respected
                case '5': directScore = 10; break; // All 5 aspects respected (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg16_checks'] || [];
            // if(peaceSummaryValue === '5' && checks.length >= 5) {
            //    bonusScore = 1; // Example: Small bonus for confirming all details
            // }
        } else if (sdgId === 'sdg-17') {
            // Score based on the partnership summary radio button
            const partnershipSummaryValue = sdgInputData.inputs['sdg17_partnership_summary'];
            switch (partnershipSummaryValue) {
                case '0': directScore = 0; break;   // None
                case '1': directScore = 2; break;   // 1 aspect matches
                case '2': directScore = 4; break;   // 2 aspects match
                case '3': directScore = 6; break;   // 3 aspects match
                case '4': directScore = 7.5; break; // 4 aspects match
                case '5': directScore = 9; break;   // 5 aspects match
                case '6': directScore = 10; break;  // All 6 aspects match (Max score)
                default: directScore = 0; break;    // Other / Not selected
            }
            // Optional Bonus:
            // const checks = sdgInputData.inputs['sdg17_checks'] || [];
            // if (partnershipSummaryValue === '6' && checks.length >= 6) {
            //     bonusScore = 1;
            // }
        } else if (sdgId === 'sdg-18') {
            // Score based on the innovation/infrastructure summary radio button
            const innovationSummaryValue = sdgInputData.inputs['sdg18_innovation_summary'];
            switch (innovationSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 1.5; break; // 1 aspect addressed
                case '2': directScore = 3.5; break; // 2 aspects addressed
                case '3': directScore = 5.5; break; // 3 aspects addressed
                case '4': directScore = 7.5; break; // 4 aspects addressed
                case '5': directScore = 10; break;  // All 5 aspects addressed (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg18_checks'] || [];
            // if (innovationSummaryValue === '5' && (checks.includes('innovate_process') || checks.includes('renovation')) ) {
            //    bonusScore = 1; // Example: Bonus for specific high-impact items within the 'all' category
            // }
        } else if (sdgId === 'sdg-19') {
            // Score based on the inclusion summary radio button
            const inclusionSummaryValue = sdgInputData.inputs['sdg19_inclusion_summary'];
            switch (inclusionSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 1.5; break; // 1 aspect respected
                case '2': directScore = 3.5; break; // 2 aspects respected
                case '3': directScore = 5.5; break; // 3 aspects respected
                case '4': directScore = 7.5; break; // 4 aspects respected
                case '5': directScore = 10; break;  // All 5 aspects respected (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg19_checks'] || [];
            // if(inclusionSummaryValue === '5' && checks.length >= 5) {
            //     bonusScore = 1; // Small bonus for explicitly ticking all details
            // }
        } else if (sdgId === 'sdg-20') {
            // Score based on the sustainability summary radio button
            const sustainabilitySummaryValue = sdgInputData.inputs['sdg20_measures'];
            switch (sustainabilitySummaryValue) {
                case 'none': directScore = 0; break;  // None
                case 'one': directScore = 1.5; break; // 1 aspect respected
                case 'two': directScore = 3.5; break; // 2 aspects respected
                case 'three': directScore = 5.5; break; // 3 aspects respected
                case 'four': directScore = 7.5; break; // 4 aspects respected
                case 'five': directScore = 10; break;  // All 5 aspects respected (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg20_checks'] || [];
            // if(sustainabilitySummaryValue === 'five' && checks.length >= 5) {
            //    bonusScore = 1; // Example: Small bonus for confirming all details
            // }
        } else if (sdgId === 'sdg-21') {
            // Score based on the consumption/production summary radio button
            const consumptionSummaryValue = sdgInputData.inputs['sdg21_consumption_summary'];
            switch (consumptionSummaryValue) {
                case '0': directScore = 0; break;   // None
                case '1': directScore = 1.5; break; // 1 aspect respected
                case '2': directScore = 3; break;   // 2 aspects respected
                case '3': directScore = 5; break;   // 3 aspects respected
                case '4': directScore = 7; break;   // 4 aspects respected
                case '5': directScore = 8.5; break; // 5 aspects respected
                case '6': directScore = 10; break;  // All 6 aspects respected (Max score)
                default: directScore = 0; break;    // Other / Not selected
            }
             // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
             // const checks = sdgInputData.inputs['sdg21_checks'] || [];
             // if(consumptionSummaryValue === '6' && checks.length >= 6) {
             //    bonusScore = 1; // Example: Small bonus for confirming all details
             // }
        } else if (sdgId === 'sdg-22') {
            // Score based on the innovation/infrastructure summary radio button
            const innovationSummaryValue = sdgInputData.inputs['sdg22_innovation_summary'];
            switch (innovationSummaryValue) {
                case '0': directScore = 0; break;  // None
                case '1': directScore = 1.5; break; // 1 aspect addressed
                case '2': directScore = 3.5; break; // 2 aspects addressed
                case '3': directScore = 5.5; break; // 3 aspects addressed
                case '4': directScore = 7.5; break; // 4 aspects addressed
                case '5': directScore = 10; break;  // All 5 aspects addressed (Max score)
                default: directScore = 0; break;   // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg22_checks'] || [];
            // if (innovationSummaryValue === '5' && (checks.includes('innovate_process') || checks.includes('renovation')) ) {
            //    bonusScore = 1; // Example: Bonus for specific high-impact items within the 'all' category
            // }
        } else if (sdgId === 'sdg-23') {
            // Score based on the marine pollution summary radio button
            const pollutionSummaryValue = sdgInputData.inputs['sdg23_pollution_summary'];
            switch (pollutionSummaryValue) {
                case '0': directScore = 0; break;   // None
                case '1': directScore = 1.5; break; // 1 aspect respected
                case '2': directScore = 3.5; break; // 2 aspects respected
                case '3': directScore = 5.5; break; // 3 aspects respected
                case '4': directScore = 7.5; break; // 4 aspects respected
                case '5': directScore = 10; break;  // All 5 aspects respected (Max score)
                default: directScore = 0; break;    // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg23_checks'] || [];
            // if(pollutionSummaryValue === '5' && checks.length >= 5) {
            //    bonusScore = 1; // Example: Small bonus for confirming all details
            // }
        } else if (sdgId === 'sdg-24') {
            let score_ecosystem = 0;
            let score_artificialisation = 0;

            // Score Part 1: Ecosystem Actions Summary (Max 5 points)
            const ecosystemSummaryValue = sdgInputData.inputs['sdg24_ecosystem_summary'];
            switch (ecosystemSummaryValue) {
                case '0': score_ecosystem = 0; break;
                case '1': score_ecosystem = 1; break;
                case '2': score_ecosystem = 2; break;
                case '3': score_ecosystem = 3; break;
                case '4': score_ecosystem = 4; break;
                case '5': score_ecosystem = 5; break; // Max for this part
                default: score_ecosystem = 0; break;
            }

            // Score Part 2: Land Artificialisation Ratio (Max 5 points)
            const artificialisationRatio = sdgInputData.inputs['sdg24_artificialisation_ratio'];
            switch (artificialisationRatio) {
                case '100': score_artificialisation = 0; break;
                case '80': score_artificialisation = 1; break;
                case '60': score_artificialisation = 2; break;
                case '40': score_artificialisation = 3; break;
                case '20': score_artificialisation = 4; break;
                case '0': score_artificialisation = 5; break; // Max for this part (100% renaturation)
                default: score_artificialisation = 0; break;
            }

            // Combine scores
            directScore = score_ecosystem + score_artificialisation;
            // Optional Bonus: Could add bonus for specific checks if needed
        } else if (sdgId === 'sdg-25') {
            // Score based on the peace/justice/institutions summary radio button
            const peaceSummaryValue = sdgInputData.inputs['sdg25_peace_summary'];
            switch (peaceSummaryValue) {
                case '0': directScore = 0; break;   // None
                case '1': directScore = 1.5; break; // 1 aspect respected
                case '2': directScore = 3.5; break; // 2 aspects respected
                case '3': directScore = 5.5; break; // 3 aspects respected
                case '4': directScore = 7.5; break; // 4 aspects respected
                case '5': directScore = 10; break;  // All 5 aspects respected (Max score)
                default: directScore = 0; break;    // Other / Not selected
            }
            // Optional Bonus: Could add bonus based on specific checkboxes ticked or comments
            // const checks = sdgInputData.inputs['sdg25_checks'] || [];
            // if(peaceSummaryValue === '5' && checks.length >= 5) {
            //    bonusScore = 1; // Example: Small bonus for confirming all details
            // }
        } else if (sdgId === 'sdg-26') {
            // Score based on the partnership summary radio button
            const partnershipSummaryValue = sdgInputData.inputs['sdg26_partnership_summary'];
            switch (partnershipSummaryValue) {
                case '0': directScore = 0; break;   // None
                case '1': directScore = 1.5; break; // 1 aspect matches
                case '2': directScore = 3; break;   // 2 aspects match
                case '3': directScore = 5; break;   // 3 aspects match
                case '4': directScore = 7; break;   // 4 aspects match
                case '5': directScore = 8.5; break; // 5 aspects match
                case '6': directScore = 10; break;  // All 6 aspects match (Max score)
                default: directScore = 0; break;    // Other / Not selected
            }
            // Optional Bonus:
            // const checks = sdgInputData.inputs['sdg26_checks'] || [];
            // if (partnershipSummaryValue === '6' && checks.length >= 6) {
            //     bonusScore = 1;
            // }
        } else if (sdgId === 'sdg-27') {
            const innovationSummaryValue = sdgInputData.inputs['sdg27_innovation_summary'];
            switch (innovationSummaryValue) {
                case '0': directScore = 0; break;
                case '1': directScore = 1.5; break;
                case '2': directScore = 3.5; break;
                case '3': directScore = 5.5; break;
                case '4': directScore = 7.5; break;
                case '5': directScore = 10; break;
                default: directScore = 0; break;
            }
        }
        // --- TODO: Add scoring logic for SDGs 18-27 ---


        // --- Normalize/Cap Score ---
        let totalScore = directScore + bonusScore;
        totalScore = Math.min(totalScore, maxScorePerSdg);
        totalScore = Math.max(totalScore, 0);

        scores.push({
            number: i,
            name: SDG_INFO[i]?.name || `SDG ${i}`,
            color_code: SDG_INFO[i]?.color_code || SDG_INFO[i]?.color || '#CCCCCC',
            total_score: parseFloat(totalScore.toFixed(1)),
            notes: sdgInputData.notes || ''
        });
    }
    return scores;
}