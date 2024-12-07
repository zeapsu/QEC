from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector

import pygame
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

import io
import sys

class QuantumStateRenderer:
    def __init__(self):
        # Initialize matplotlib settings for LaTeX
        plt.rcParams.update({
            "text.usetex": True,
            "font.family": "serif",
            "font.serif": ["Computer Modern Roman"],
        })
        
    def state_to_latex(self, statevector):
        """Convert statevector to LaTeX string."""
        # Round small values to zero to avoid numerical noise
        state = np.array(statevector)
        state = np.where(np.abs(state) < 1e-10, 0, state)
        
        # Build LaTeX string
        terms = []
        basis_states = [r'|00\rangle', r'|01\rangle', r'|10\rangle', r'|11\rangle']
        
        for amp, basis in zip(state, basis_states):
            if abs(amp) < 1e-10:
                continue
                
            # Format complex number
            if np.isreal(amp) and abs(amp.imag) < 1e-10:
                coeff = f"{amp.real:.2f}".rstrip('0').rstrip('.')
            else:
                coeff = f"({amp.real:.2f}{'+' if amp.imag >= 0 else ''}{amp.imag:.2f}i)".rstrip('0').rstrip('.')
                
            # Skip coefficient of 1
            if coeff == "1":
                terms.append(basis)
            else:
                terms.append(f"{coeff}{basis}")
                
        if not terms:
            return r"|\psi\rangle = 0"
            
        return r"|\psi\rangle = " + " + ".join(terms)

    def render_state(self, statevector, width=600, height=100):
        """Render statevector as LaTeX and return pygame surface."""
        # Create figure and render LaTeX
        fig = Figure(figsize=(width/100, height/100), dpi=100)
        fig.patch.set_alpha(0)
        ax = fig.add_subplot(111)
        ax.set_axis_off()
        
        # Render LaTeX equation
        latex_str = self.state_to_latex(statevector)
        ax.text(0.5, 0.5, latex_str, 
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes)
        
        # Convert to pygame surface
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        
        # Get the RGBA buffer from the figure
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        
        # Load buffer into pygame image
        image = pygame.image.load(buf)
        buf.close()
        plt.close(fig)
        
        return image

class QuantumVisualizer:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Quantum Circuit Visualizer")
        
        # Initialize state renderer
        self.state_renderer = QuantumStateRenderer()
        
        # Colors and parameters (as before)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.qubit_spacing = 80
        self.gate_width = 40
        self.gate_height = 40
        
    def run_simulation(self):
        try:
            # Create and simulate circuit (as before)
            circuit = QuantumCircuit(2)
            circuit.cx(0, 1)
            statevector = Statevector.from_instruction(circuit)
            
            # Main loop
            clock = pygame.time.Clock()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                
                # Clear screen
                self.screen.fill(self.WHITE)
                
                # Draw quantum wires (as before)
                for i in range(2):
                    self.draw_quantum_wire(200 + i * self.qubit_spacing)
                
                # Draw CNOT gate (as before)
                self.draw_cnot(200, 200 + self.qubit_spacing, 400)
                
                # Render state vector with LaTeX
                state_surface = self.state_renderer.render_state(statevector.data)
                state_rect = state_surface.get_rect(center=(self.width//2, 50))
                self.screen.blit(state_surface, state_rect)
                
                pygame.display.flip()
                clock.tick(60)
                
        finally:
            pygame.quit()

if __name__ == "__main__":
    visualizer = QuantumVisualizer()
    visualizer.run_simulation()