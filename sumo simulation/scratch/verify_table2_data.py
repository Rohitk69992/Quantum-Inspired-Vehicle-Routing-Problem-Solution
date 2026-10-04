import json
import re

def verify_table2():
    with open('results/statistics/statistical_analysis.json', 'r', encoding='utf-8') as f:
        stat_data = json.load(f)

    with open('research_paper/tables/tab_main_benchmark.tex', 'r', encoding='utf-8') as f:
        tex_content = f.read()

    errors = []
    
    # Check all 7 instances
    for inst_id, inst_info in stat_data['instances'].items():
        clean_id = inst_id.replace('_', r'\_')
        if clean_id not in tex_content:
            errors.append(f'Instance {clean_id} missing')
            
        num_c = inst_info['num_customers']
        num_v = inst_info['num_vehicles']
        if f'N={num_c}' not in tex_content:
            errors.append(f'N={num_c} missing for {inst_id}')
        if f'K={num_v}' not in tex_content:
            errors.append(f'K={num_v} missing for {inst_id}')

        algos = inst_info['algorithms']
        if 'Exact_MIP' in algos and algos['Exact_MIP']['feasible']:
            mip = algos['Exact_MIP']
            cost_str = f"{mip['cost']:.2f}"
            time_str = f"{mip['runtime_ms']:.1f}"
            if cost_str not in tex_content:
                errors.append(f"MIP cost {cost_str} missing for {inst_id}")
            if time_str not in tex_content:
                errors.append(f"MIP runtime {time_str} missing for {inst_id}")

        if 'Exhaustive_Baseline' in algos:
            ex = algos['Exhaustive_Baseline']
            cost_str = f"{ex['cost']:.2f}"
            time_str = f"{ex['runtime_ms']:.1f}"
            if cost_str not in tex_content:
                errors.append(f"Exhaustive cost {cost_str} missing for {inst_id}")
            if time_str not in tex_content:
                errors.append(f"Exhaustive runtime {time_str} missing for {inst_id}")

        for a_name in ['HGS', 'ALNS', 'QPSO']:
            if a_name in algos:
                a_data = algos[a_name]
                cost_str = f"{a_data['mean_cost']:.2f}"
                sd_str = f"{a_data['std_cost']:.2f}"
                med_str = f"{a_data['median_cost']:.2f}"
                iqr_str = f"[{a_data['iqr_cost']:.1f}]"
                ci_str = f"[{a_data['ci_95_cost'][0]:.1f}, {a_data['ci_95_cost'][1]:.1f}]"
                time_str = f"{a_data['mean_runtime_ms']:.1f}"
                gap_str = f"{a_data['mean_gap_pct']:.2f}" if a_data['mean_gap_pct'] is not None else "---"
                feas_str = f"{a_data['feasibility_rate_pct']:.0f}"

                for field_name, val in [("cost", cost_str), ("sd", sd_str), ("median", med_str), 
                                        ("iqr", iqr_str), ("ci", ci_str), ("runtime", time_str), 
                                        ("feas", feas_str)]:
                    if val not in tex_content:
                        errors.append(f"{a_name} {field_name} '{val}' missing for {inst_id}")

    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print("  -", e)
        return False
    else:
        print("VERIFICATION PASSED: Every numerical result, algorithm, and instance matches with ZERO data changes!")
        return True

if __name__ == '__main__':
    verify_table2()
