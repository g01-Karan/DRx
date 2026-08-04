"""
==============================================================================
Rehabilitation Recommendation Engine
==============================================================================
Knowledge-based ML recommendation system that generates rehabilitation
guidance based on fracture prediction results. Provides exercises, recovery
stages, physiotherapy guidance, precautions, and follow-up schedules.
==============================================================================
"""


def get_rehabilitation_plan(prediction, severity, confidence):
    """
    Generate a comprehensive rehabilitation plan based on prediction results.

    Args:
        prediction (str): 'Fractured' or 'Not Fractured'
        severity (str): 'Low', 'Moderate', 'High', or 'Critical'
        confidence (float): Prediction confidence percentage

    Returns:
        dict: Complete rehabilitation plan with exercises, stages, etc.
    """
    pred_clean = str(prediction).strip().lower()
    if pred_clean in ['not fractured', 'normal']:
        return _get_normal_plan()

    # Generate plan based on severity level
    severity_plans = {
        'Low': _get_low_severity_plan(),
        'Moderate': _get_moderate_severity_plan(),
        'High': _get_high_severity_plan(),
        'Critical': _get_critical_severity_plan()
    }

    plan = severity_plans.get(severity, _get_moderate_severity_plan())
    plan['disclaimer'] = (
        'This is an AI-generated rehabilitation guidance for educational purposes only. '
        'Always consult your physician or a qualified orthopedic specialist before '
        'following any exercise program or rehabilitation plan.'
    )
    return plan


def _get_normal_plan():
    """Plan for non-fractured (normal) X-ray results."""
    return {
        'summary': 'No fracture detected. You are healthy and doing great! No rehabilitation, exercises, or precautions are required. Keep maintaining your general fitness and bone health through regular activity.',
        'exercises': [],
        'recovery_stages': [],
        'physiotherapy': None,
        'precautions': [],
        'followup_schedule': [],
        'disclaimer': (
            'This is an AI-generated guidance for educational purposes only. '
            'Always consult your physician for personalized medical advice.'
        )
    }


def _get_low_severity_plan():
    """Rehabilitation plan for low severity fractures (hairline/stress fractures)."""
    return {
        'summary': 'Mild fracture detected. Expected recovery with rest and gradual rehabilitation.',
        'exercises': [
            {
                'name': 'Isometric Exercises',
                'description': 'Gentle muscle contractions without joint movement to prevent atrophy.',
                'duration': '5-10 minutes, 3x daily',
                'icon': 'muscle'
            },
            {
                'name': 'Range of Motion (ROM)',
                'description': 'Slow, controlled movements to maintain joint flexibility.',
                'duration': '10 minutes, 2x daily (after Week 2)',
                'icon': 'stretch'
            },
            {
                'name': 'Gentle Resistance Training',
                'description': 'Light resistance bands to gradually rebuild strength.',
                'duration': '15 minutes, daily (after Week 4)',
                'icon': 'resistance'
            },
            {
                'name': 'Pool Therapy (Hydrotherapy)',
                'description': 'Low-impact exercises in warm water to aid recovery.',
                'duration': '20-30 minutes, 3x weekly (after Week 4)',
                'icon': 'pool'
            }
        ],
        'recovery_stages': [
            {
                'stage': 'Immobilization & Rest',
                'timeline': 'Week 1–2',
                'description': 'Complete rest with immobilization (cast/brace). Focus on pain management and reducing swelling.',
                'activities': ['Ice application', 'Elevation', 'Pain medication as prescribed', 'Gentle isometric exercises']
            },
            {
                'stage': 'Early Mobilization',
                'timeline': 'Week 3–4',
                'description': 'Begin gentle range-of-motion exercises. Gradually increase activity under guidance.',
                'activities': ['ROM exercises', 'Light stretching', 'Guided physiotherapy sessions']
            },
            {
                'stage': 'Strengthening',
                'timeline': 'Week 5–6',
                'description': 'Progress to resistance training and weight-bearing exercises as tolerated.',
                'activities': ['Resistance bands', 'Light weight training', 'Balance exercises']
            },
            {
                'stage': 'Return to Activity',
                'timeline': 'Week 7–8',
                'description': 'Gradual return to normal activities. Continue strengthening exercises.',
                'activities': ['Progressive walking', 'Full ROM exercises', 'Sport-specific training']
            }
        ],
        'physiotherapy': 'Recommended 2-3 sessions per week starting from Week 3. Focus on joint mobility, muscle strengthening, and gradual weight-bearing progression.',
        'precautions': [
            {'type': 'do', 'text': 'Keep the affected area elevated when resting'},
            {'type': 'do', 'text': 'Apply ice for 15-20 minutes every 2-3 hours for first 48 hours'},
            {'type': 'do', 'text': 'Follow prescribed medication schedule'},
            {'type': 'do', 'text': 'Attend all follow-up appointments'},
            {'type': 'dont', 'text': 'Do not apply heat in the first 72 hours'},
            {'type': 'dont', 'text': 'Avoid putting full weight on the affected area prematurely'},
            {'type': 'dont', 'text': 'Do not remove cast/brace without medical approval'},
            {'type': 'dont', 'text': 'Avoid high-impact activities until fully healed'}
        ],
        'followup_schedule': [
            {'week': 'Week 1', 'action': 'Initial follow-up X-ray and assessment'},
            {'week': 'Week 3', 'action': 'Check healing progress, begin physiotherapy'},
            {'week': 'Week 6', 'action': 'Follow-up X-ray to confirm bone union'},
            {'week': 'Week 8', 'action': 'Final assessment and clearance for normal activity'}
        ]
    }


def _get_moderate_severity_plan():
    """Rehabilitation plan for moderate severity fractures."""
    return {
        'summary': 'Moderate fracture detected. Structured rehabilitation required for full recovery.',
        'exercises': [
            {
                'name': 'Isometric Muscle Activation',
                'description': 'Static muscle contractions to prevent atrophy during immobilization.',
                'duration': '5 minutes, 4x daily',
                'icon': 'muscle'
            },
            {
                'name': 'Passive Range of Motion',
                'description': 'Assisted gentle movements to maintain joint health.',
                'duration': '10 minutes, 2x daily (after Week 3)',
                'icon': 'stretch'
            },
            {
                'name': 'Active Range of Motion',
                'description': 'Self-directed movement exercises within pain-free range.',
                'duration': '15 minutes, 2x daily (after Week 5)',
                'icon': 'stretch'
            },
            {
                'name': 'Progressive Resistance',
                'description': 'Graduated strength training with bands and light weights.',
                'duration': '20 minutes, daily (after Week 7)',
                'icon': 'resistance'
            },
            {
                'name': 'Balance & Proprioception',
                'description': 'Balance board exercises to restore coordination and stability.',
                'duration': '10 minutes, daily (after Week 8)',
                'icon': 'balance'
            }
        ],
        'recovery_stages': [
            {
                'stage': 'Acute Phase & Immobilization',
                'timeline': 'Week 1–3',
                'description': 'Complete immobilization with cast/splint. Pain and swelling management. Gentle isometric exercises only.',
                'activities': ['RICE protocol', 'Isometric exercises', 'Upper/lower body mobility (unaffected areas)']
            },
            {
                'stage': 'Protected Mobilization',
                'timeline': 'Week 4–6',
                'description': 'Transition to removable brace. Begin passive ROM exercises under physiotherapy supervision.',
                'activities': ['Passive ROM', 'Gentle stretching', 'Pool therapy if available']
            },
            {
                'stage': 'Active Rehabilitation',
                'timeline': 'Week 7–9',
                'description': 'Active exercises and progressive loading. Strength and endurance training.',
                'activities': ['Active ROM', 'Resistance training', 'Functional exercises']
            },
            {
                'stage': 'Advanced Strengthening',
                'timeline': 'Week 10–12',
                'description': 'Full weight-bearing. Advanced strength and coordination training.',
                'activities': ['Full weight-bearing', 'Balance exercises', 'Sport-specific drills']
            },
            {
                'stage': 'Return to Full Activity',
                'timeline': 'Week 12+',
                'description': 'Gradual return to all normal activities and sports.',
                'activities': ['Progressive activity resumption', 'Continued strengthening', 'Performance testing']
            }
        ],
        'physiotherapy': 'Recommended 3 sessions per week from Week 4 onwards. Focus on restoring full range of motion, building strength progressively, and retraining functional movement patterns.',
        'precautions': [
            {'type': 'do', 'text': 'Strictly follow immobilization instructions'},
            {'type': 'do', 'text': 'Apply ice regularly during the acute phase'},
            {'type': 'do', 'text': 'Attend physiotherapy sessions consistently'},
            {'type': 'do', 'text': 'Ensure adequate protein and calcium intake'},
            {'type': 'do', 'text': 'Report any increase in pain or swelling immediately'},
            {'type': 'dont', 'text': 'Do not bear weight without medical clearance'},
            {'type': 'dont', 'text': 'Avoid sudden movements or twisting'},
            {'type': 'dont', 'text': 'Do not skip follow-up appointments'},
            {'type': 'dont', 'text': 'Avoid smoking — it significantly delays bone healing'},
            {'type': 'dont', 'text': 'Do not return to sports without complete clearance'}
        ],
        'followup_schedule': [
            {'week': 'Week 1', 'action': 'Post-injury X-ray and immobilization check'},
            {'week': 'Week 3', 'action': 'Follow-up X-ray, assess healing progress'},
            {'week': 'Week 6', 'action': 'X-ray review, possible brace removal'},
            {'week': 'Week 9', 'action': 'Strength assessment and rehab progress review'},
            {'week': 'Week 12', 'action': 'Final X-ray, clearance for full activity'}
        ]
    }


def _get_high_severity_plan():
    """Rehabilitation plan for high severity fractures."""
    plan = _get_moderate_severity_plan()
    plan['summary'] = 'Significant fracture detected. Comprehensive rehabilitation with specialist supervision required.'
    plan['recovery_stages'][0]['timeline'] = 'Week 1–4'
    plan['recovery_stages'][0]['description'] = 'Extended immobilization period. Surgical intervention may be required. Strict rest and pain management.'
    plan['recovery_stages'][1]['timeline'] = 'Week 5–8'
    plan['recovery_stages'][2]['timeline'] = 'Week 9–12'
    plan['recovery_stages'][3]['timeline'] = 'Week 13–16'
    plan['recovery_stages'][4]['timeline'] = 'Week 16+'
    plan['physiotherapy'] = 'Intensive physiotherapy recommended 3-4 sessions per week from Week 5 onwards. Specialist-supervised recovery with focus on preventing complications such as joint stiffness and muscle atrophy.'
    plan['followup_schedule'] = [
        {'week': 'Week 1', 'action': 'Emergency orthopedic consultation and imaging'},
        {'week': 'Week 2', 'action': 'Post-treatment/surgical follow-up'},
        {'week': 'Week 4', 'action': 'X-ray review, immobilization assessment'},
        {'week': 'Week 8', 'action': 'Healing progress X-ray, begin active rehab'},
        {'week': 'Week 12', 'action': 'Comprehensive strength and ROM assessment'},
        {'week': 'Week 16', 'action': 'Final clearance evaluation'}
    ]
    return plan


def _get_critical_severity_plan():
    """Rehabilitation plan for critical severity fractures."""
    plan = _get_high_severity_plan()
    plan['summary'] = 'Critical fracture detected. Immediate specialist care and surgical evaluation required. Extended rehabilitation timeline.'
    plan['recovery_stages'][0]['timeline'] = 'Week 1–6'
    plan['recovery_stages'][0]['description'] = 'Emergency care and likely surgical intervention. Post-operative immobilization. Intensive pain management and infection prevention.'
    plan['recovery_stages'][1]['timeline'] = 'Week 7–10'
    plan['recovery_stages'][2]['timeline'] = 'Week 11–16'
    plan['recovery_stages'][3]['timeline'] = 'Week 17–22'
    plan['recovery_stages'][4]['timeline'] = 'Week 22+'
    plan['physiotherapy'] = 'Intensive specialist physiotherapy required 4-5 sessions per week after surgical clearance. Long-term rehabilitation focusing on functional recovery, preventing complications, and restoring quality of life.'
    plan['followup_schedule'] = [
        {'week': 'Immediate', 'action': 'Emergency orthopedic surgery consultation'},
        {'week': 'Week 1', 'action': 'Post-operative assessment'},
        {'week': 'Week 3', 'action': 'Wound check and X-ray'},
        {'week': 'Week 6', 'action': 'Cast/fixation review'},
        {'week': 'Week 10', 'action': 'Healing assessment, begin active rehab'},
        {'week': 'Week 16', 'action': 'Progress evaluation'},
        {'week': 'Week 22', 'action': 'Final clearance assessment'}
    ]
    return plan
