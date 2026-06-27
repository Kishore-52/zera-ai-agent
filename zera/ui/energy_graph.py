import graphviz
from zera.schemas import SensorReading

def generate_energy_map(scenario: str, sensor_data: SensorReading):
    dot = graphviz.Digraph(comment='Energy Hazard Graph')
    dot.attr(rankdir='TB', size='8,8')
    dot.attr('node', shape='box', style='filled', fontname='Helvetica')

    # Status colors
    COLOR_VERIFIED = '#d4edda' # Light green
    COLOR_ISOLATED = '#cce5ff' # Light blue
    COLOR_RESIDUAL = '#f8d7da' # Light red
    COLOR_MISSING = '#fff3cd'  # Light yellow
    COLOR_PENDING = '#e2e3e5'  # Light grey

    # Main machine
    dot.node('M', 'Hydraulic Press HP-01', fillcolor='white', shape='cylinder')

    # Electrical
    elec_color = COLOR_VERIFIED if sensor_data.breaker_lock_verified else COLOR_MISSING
    dot.node('E', 'Electrical Energy', fillcolor=elec_color)
    dot.node('E1', 'Main Breaker', fillcolor=elec_color)
    dot.node('E2', 'Control Circuit', fillcolor=elec_color)
    dot.edge('M', 'E')
    dot.edge('E', 'E1')
    dot.edge('E', 'E2')

    # Hydraulic
    hyd_color = COLOR_VERIFIED if sensor_data.hydraulic_pressure <= 1.0 else COLOR_RESIDUAL
    dot.node('H', 'Hydraulic Energy', fillcolor=hyd_color)
    dot.node('H1', 'Hydraulic Pump', fillcolor=COLOR_VERIFIED if sensor_data.hydraulic_isolation_valve_verified else COLOR_MISSING)
    dot.node('H2', 'Accumulator', fillcolor=hyd_color)
    dot.node('H3', 'Press Cylinder', fillcolor=hyd_color)
    dot.edge('M', 'H')
    dot.edge('H', 'H1')
    dot.edge('H', 'H2')
    dot.edge('H', 'H3')

    # Pneumatic
    pneu_color = COLOR_VERIFIED if sensor_data.pneumatic_pressure <= 1.0 else COLOR_RESIDUAL
    dot.node('P', 'Pneumatic Energy', fillcolor=pneu_color)
    dot.node('P1', 'Workpiece Clamp', fillcolor=pneu_color)
    dot.edge('M', 'P')
    dot.edge('P', 'P1')

    # Mechanical/Gravitational
    mech_color = COLOR_VERIFIED
    ram_color = COLOR_VERIFIED
    block_color = COLOR_VERIFIED
    if sensor_data.ram_position.lower() == 'raised':
        if not sensor_data.mechanical_block_installed:
            mech_color = COLOR_MISSING
            ram_color = COLOR_MISSING
            block_color = COLOR_MISSING
            
    dot.node('G', 'Mechanical & Gravitational', fillcolor=mech_color)
    dot.node('G1', 'Raised Ram', fillcolor=ram_color)
    dot.node('G2', 'Mechanical Safety Block', fillcolor=block_color)
    dot.edge('M', 'G')
    dot.edge('G', 'G1')
    dot.edge('G', 'G2')

    # Legend
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(label='State Legend')
        c.node('L1', 'VERIFIED / SAFE', fillcolor=COLOR_VERIFIED)
        c.node('L2', 'RESIDUAL ENERGY', fillcolor=COLOR_RESIDUAL)
        c.node('L3', 'EVIDENCE MISSING', fillcolor=COLOR_MISSING)
        c.node('L4', 'ISOLATED', fillcolor=COLOR_ISOLATED)

    return dot
