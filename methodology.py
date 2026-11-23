"""Explicit ordinal anchors; never aggregate these into a fake precision score."""
RUBRIC = {
 'Stakeholder value': {'High':'Directly addresses a documented priority with a measurable stakeholder outcome.', 'Medium':'Plausible indirect benefit; affected users or outcome still need validation.', 'Low':'Weak connection to the stated problem or documented stakeholder need.'},
 'Business value': {'High':'Relevant measured economic evidence plus a credible local value mechanism.', 'Medium':'Plausible cost/revenue mechanism; local baseline and economics unvalidated.', 'Low':'No credible economic mechanism or costs likely dominate the proposed benefit.'},
 'Technical feasibility': {'High':'Relevant real-world deployments or strong pilots demonstrate the application.', 'Medium':'Working prototype or adjacent deployment; substantial integration remains.', 'Low':'Primarily theoretical or laboratory evidence for this application.'},
 'Technology maturity': {'High':'Repeated commercial deployment for this application.', 'Medium':'Demonstrated prototype, pilot, or early commercialization.', 'Low':'Academic research or laboratory prototype.'},
 'Implementation difficulty': {'High':'Major integration, qualification, capital, or workflow changes needed.', 'Medium':'Bounded integration and training with known dependencies.', 'Low':'Routine configuration with existing capabilities and minimal workflow change.'},
 'Differentiation': {'High':'Evidence supports a defensible capability, exclusive asset, or hard-to-copy advantage.', 'Medium':'Potential temporary advantage; imitability or competitor adoption unclear.', 'Low':'Widely available capability mainly supports parity or operational improvement.'},
 'Evidence strength': {'High':'Multiple independent, directly relevant empirical sources support the application.', 'Medium':'One directly relevant empirical source or several adjacent primary sources.', 'Low':'Concepts, vendor claims, simulations, or weakly transferable evidence only.'},
 'Human impact': {'High':'Substantial changes to authority, workload, skills, or livelihoods.', 'Medium':'New tasks or training; existing accountability can be retained.', 'Low':'Minor workflow changes with little effect on roles or decision authority.'},
 'Risk': {'High':'Material unresolved safety, privacy, regulatory, or business failure exposure.', 'Medium':'Material risks with plausible controls requiring validation.', 'Low':'Limited, reversible exposure with established controls.'},
 'Time to implementation': {'High':'Estimated over 3 years to scoped deployment; major dependencies remain.', 'Medium':'Estimated 1–3 years to scoped deployment with dependencies.', 'Low':'Estimated under 1 year to scoped deployment with existing capabilities.'}
}
UNKNOWN = 'Unknown: approved evidence is insufficient to select an anchor. State what evidence is missing.'
EVIDENCE_ANCHORS = {'High':'Direct primary empirical evidence relevant to the precise finding; method and limitations disclosed.', 'Medium':'Credible primary description or adjacent empirical result; transfer or outcome unverified.', 'Low':'Marketing claim, concept, indirect source, or poorly supported inference.'}

def rubric_markdown():
    rows = ['| Dimension | High | Medium | Low |','|---|---|---|---|']
    rows += [f"| {d} | {v['High']} | {v['Medium']} | {v['Low']} |" for d,v in RUBRIC.items()]
    return '\n'.join(rows) + '\n\n' + UNKNOWN + '\n\nHigh is not always desirable: difficulty, human impact, risk and time describe burden or exposure. No overall numerical score is calculated. Ratings are model judgments against anchors, not independently verified measurements.'
