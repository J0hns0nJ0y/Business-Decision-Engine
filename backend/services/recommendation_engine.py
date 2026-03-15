def generate_recommendations(df, insights):
    
    recommendations = []

    best_channel = insights["best_channel"]
    worst_channel = insights["worst_channel"]
    overall_roi = insights["overall_roi"]
    growth = insights["avg_growth"]

    # Channel recommendations
    recommendations.append(
        f"Increase investment in {best_channel} as it's the highest ROI channel."
    )

    recommendations.append(
        f"Reduce spending on {worst_channel} as it's the lowest performing channel."
    )

    # ROI recommendation
    if overall_roi > 1:
        recommendations.append(
            "Marketing campaigns are profitable. Consider scaling budget."
        )
    else:
        recommendations.append(
            "Marketing ROI is weak. Campaign optimization recommended."
        )

    # Growth recommendation
    if growth > 0:
        recommendations.append(
            "Revenue trend is growing. Current strategy shows positive momentum."
        )
    else:
        recommendations.append(
            "Revenue growth is declining. Investigate campaign performance."
        )

    return recommendations