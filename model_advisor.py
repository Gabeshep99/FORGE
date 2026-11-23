"""Model and per-stage token profiles. Suggestions are hypotheses, not benchmark results."""
from cost_control import PRICES

MODEL_OPTIONS = ('gpt-6-luna', 'gpt-6.1-terra', 'gpt-6.1-sol', 'gpt-6-astra')
STAGES = ('Researcher/search','Researcher/extract','Strategist/opportunities','Strategist/roadmap','Critic')
PROFILES = {
    'Budget saver': {
        'models': {'Researcher':'gpt-6.1-terra', 'Strategist':'gpt-6.1-terra', 'Critic':'gpt-6-luna'},
        'caps': (5000,7000,13000,12000,11000),
        'reasoning': 'low',
        'note': 'Lowest-cost recommended starting point; Luna critic may need extra quality review.'},
    'Balanced (recommended)': {
        'models': {'Researcher':'gpt-6.1-terra', 'Strategist':'gpt-6.1-sol', 'Critic':'gpt-6.1-terra'},
        'caps': (6000,8500,16000,14000,13000),
        'reasoning':'low',
        'note': 'Additional strategist output room with inexpensive researcher and critic.'},
    'Higher reliability': {
        'models': {'Researcher':'gpt-6.1-sol', 'Strategist':'gpt-6.1-sol', 'Critic':'gpt-6.1-sol'},
        'caps': (8000,10000,22000,18000,16000),
        'reasoning':'medium',
        'note': 'More reasoning budget and headroom; higher potential cost, not guaranteed better quality.'},
}

def profile_caps(profile):
    return dict(zip(STAGES, PROFILES[profile]['caps']))

def recommended_model(agent, priority='Balanced (recommended)'):
    return PROFILES[priority]['models'][agent]

def rough_total_cost(models, caps):
    """Worst-case output cap token price + very rough estimated input and two web-search calls."""
    # Inputs assume 7k tokens each; conservative planning heuristic, not a provider quote.
    total = 0.04  # two approximate web calls; can be exceeded
    for stage in STAGES:
        model = models[stage.split('/')[0]]
        inp,out = PRICES[model]
        total += (7000*inp + caps[stage]*out)/1_000_000
    return total

def recommended_reasoning(model, profile):
    # Terra/Luna support none, whereas Sol/Astra require low or higher.
    if model in ('gpt-6-luna', 'gpt-6.1-terra') and profile == 'Budget saver':
        return 'none'
    return PROFILES[profile]['reasoning']
