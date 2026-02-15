"""
QIMES (Quantum-Inspired Multi-Axis Ethical State Model) Framework
Implementation und Vergleich mit anderen ethischen Entscheidungsmodellen
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json


class DecisionOutcome(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    HUMAN_REVIEW = "human_review"
    BLOCKED_BY_DIGNITY = "blocked_by_dignity"


@dataclass
class EthicalScenario:
    """Repräsentiert ein ethisches Entscheidungsszenario"""
    name: str
    description: str
    harm_level: float  # 0-1, höher = mehr Schaden
    benefit_level: float  # 0-1, höher = mehr Nutzen
    context_factors: Dict[str, float]  # z.B. {"urgency": 0.8, "transparency": 0.3}
    dignity_violations: List[str]  # Liste potentieller Menschenrechtsverletzungen
    ground_truth: Optional[str] = None  # Erwartete ethische Antwort


class DignityConstraints:
    """Harte Würde-Constraints basierend auf UN-Menschenrechten"""
    
    CONSTRAINTS = {
        "no_discrimination": "Keine Diskriminierung nach Alter, Geschlecht, Herkunft, etc.",
        "privacy_protection": "Schutz der Privatsphäre und persönlicher Daten",
        "autonomy_respect": "Achtung der menschlichen Autonomie",
        "transparency": "Keine verdeckte Manipulation",
        "equal_treatment": "Gleichbehandlung bei Ressourcenverteilung",
        "dignity_as_subject": "Mensch nicht als reines Datenobjekt"
    }
    
    @staticmethod
    def check(violations: List[str]) -> Tuple[bool, List[str]]:
        """
        Prüft ob Würde-Constraints verletzt werden
        Returns: (is_valid, violated_constraints)
        """
        violated = [v for v in violations if v in DignityConstraints.CONSTRAINTS]
        return len(violated) == 0, violated


class QIMESModel:
    """
    QIMES: Quantum-Inspired Multi-Axis Ethical State Model
    
    Moralischer Zustand als Superposition in Hilbertraum:
    |ψ⟩ = √p_H|Harm⟩ + √p_B|Benefit⟩ + √p_R|Reflection⟩
    """
    
    def __init__(self, reflection_threshold: float = 0.4):
        self.reflection_threshold = reflection_threshold
        self.name = "QIMES"
        
    def _calculate_state_vector(self, scenario: EthicalScenario) -> np.ndarray:
        """
        Berechnet den moralischen Zustandsvektor |ψ⟩
        """
        # Normalisiere Harm und Benefit
        harm = scenario.harm_level
        benefit = scenario.benefit_level
        
        # Reflection-Komponente: Ambiguität und moralische Spannung
        # Hoch wenn Harm und Benefit beide signifikant sind
        reflection = harm * benefit * 2  # Maximiert wenn beide ~0.5
        
        # Normalisierung für Wahrscheinlichkeitsinterpretation
        total = harm + benefit + reflection
        if total == 0:
            total = 1
            
        p_h = harm / total
        p_b = benefit / total
        p_r = reflection / total
        
        # Zustandsvektor (normiert)
        state_vector = np.array([np.sqrt(p_h), np.sqrt(p_b), np.sqrt(p_r)])
        
        return state_vector
    
    def _apply_context_operator(self, state: np.ndarray, 
                                context: Dict[str, float]) -> np.ndarray:
        """
        Kontextoperator: Modifiziert den Zustand basierend auf Kontext
        """
        # Kontext-Matrix (vereinfachte Darstellung)
        urgency = context.get("urgency", 0.5)
        transparency = context.get("transparency", 0.5)
        social_impact = context.get("social_impact", 0.5)
        
        # Kontext beeinflusst wie stark Reflection gewichtet wird
        context_weight = np.array([
            1.0,  # Harm bleibt stabil
            1.0 + urgency * 0.3,  # Benefit erhöht bei Dringlichkeit
            1.0 + (1 - transparency) * 0.5  # Reflection erhöht bei Intransparenz
        ])
        
        modified_state = state * context_weight
        # Renormalisierung
        return modified_state / np.linalg.norm(modified_state)
    
    def decide(self, scenario: EthicalScenario) -> Tuple[DecisionOutcome, Dict]:
        """
        Hauptentscheidungsfunktion des QIMES-Modells
        """
        metadata = {
            "model": self.name,
            "scenario": scenario.name
        }
        
        # Schritt 1: Würde-Constraints prüfen (Veto-Mechanismus)
        is_valid, violated = DignityConstraints.check(scenario.dignity_violations)
        if not is_valid:
            metadata["violated_constraints"] = violated
            metadata["reason"] = "Würde-Constraint verletzt"
            return DecisionOutcome.BLOCKED_BY_DIGNITY, metadata
        
        # Schritt 2: Zustandsvektor berechnen
        state = self._calculate_state_vector(scenario)
        metadata["initial_state"] = state.tolist()
        
        # Schritt 3: Kontext anwenden
        final_state = self._apply_context_operator(state, scenario.context_factors)
        metadata["final_state"] = final_state.tolist()
        
        # Schritt 4: "Messung" - Kollaps in konkrete Entscheidung
        harm_weight, benefit_weight, reflection_weight = final_state ** 2
        
        metadata["weights"] = {
            "harm": float(harm_weight),
            "benefit": float(benefit_weight),
            "reflection": float(reflection_weight)
        }
        
        # Entscheidungslogik
        if reflection_weight > self.reflection_threshold:
            # Hohe Ambiguität → Human-in-the-Loop
            metadata["reason"] = "Hohe moralische Ambiguität - menschliche Prüfung erforderlich"
            return DecisionOutcome.HUMAN_REVIEW, metadata
        
        if benefit_weight > harm_weight * 1.5:
            metadata["reason"] = "Nutzen überwiegt Schaden deutlich"
            return DecisionOutcome.APPROVE, metadata
        elif harm_weight > benefit_weight * 1.3:
            metadata["reason"] = "Schaden überwiegt Nutzen"
            return DecisionOutcome.REJECT, metadata
        else:
            metadata["reason"] = "Ausgeglichene Situation - Prüfung erforderlich"
            return DecisionOutcome.HUMAN_REVIEW, metadata


class UtilitarianModel:
    """
    Klassisches utilitaristisches Modell: Maximiere Nutzen minus Schaden
    """
    
    def __init__(self):
        self.name = "Utilitarismus"
        
    def decide(self, scenario: EthicalScenario) -> Tuple[DecisionOutcome, Dict]:
        metadata = {
            "model": self.name,
            "scenario": scenario.name
        }
        
        # Einfache Nutzen-Kosten-Rechnung
        net_benefit = scenario.benefit_level - scenario.harm_level
        
        metadata["net_benefit"] = float(net_benefit)
        
        if net_benefit > 0.2:
            metadata["reason"] = "Positiver Nettonutzen"
            return DecisionOutcome.APPROVE, metadata
        elif net_benefit < -0.2:
            metadata["reason"] = "Negativer Nettonutzen"
            return DecisionOutcome.REJECT, metadata
        else:
            metadata["reason"] = "Grenzfall"
            return DecisionOutcome.HUMAN_REVIEW, metadata


class RuleBasedModel:
    """
    Regelbasiertes System mit festen Schwellenwerten
    """
    
    def __init__(self, harm_threshold: float = 0.6):
        self.name = "Regelbasiert"
        self.harm_threshold = harm_threshold
        
    def decide(self, scenario: EthicalScenario) -> Tuple[DecisionOutcome, Dict]:
        metadata = {
            "model": self.name,
            "scenario": scenario.name
        }
        
        # Harte Regeln
        if scenario.harm_level > self.harm_threshold:
            metadata["reason"] = f"Schaden über Schwellenwert ({self.harm_threshold})"
            return DecisionOutcome.REJECT, metadata
        
        if len(scenario.dignity_violations) > 0:
            metadata["reason"] = "Potentielle Würdeverletzung erkannt"
            metadata["violations"] = scenario.dignity_violations
            return DecisionOutcome.REJECT, metadata
        
        if scenario.benefit_level > 0.5:
            metadata["reason"] = "Ausreichender Nutzen"
            return DecisionOutcome.APPROVE, metadata
        
        metadata["reason"] = "Keine klare Regel greift"
        return DecisionOutcome.HUMAN_REVIEW, metadata


class StatisticalModel:
    """
    Statistisches Modell das nur auf Korrelationen basiert (anfällig für Bias)
    """
    
    def __init__(self):
        self.name = "Statistisch"
        
    def decide(self, scenario: EthicalScenario) -> Tuple[DecisionOutcome, Dict]:
        metadata = {
            "model": self.name,
            "scenario": scenario.name
        }
        
        # Ignoriert ethische Bedenken, optimiert nur auf statistischen Erfolg
        # Simuliert "Proxy-Variable" Problem
        success_probability = scenario.benefit_level * (1 - scenario.harm_level * 0.3)
        
        metadata["success_probability"] = float(success_probability)
        
        if success_probability > 0.6:
            metadata["reason"] = "Hohe statistische Erfolgswahrscheinlichkeit"
            return DecisionOutcome.APPROVE, metadata
        elif success_probability < 0.3:
            metadata["reason"] = "Niedrige Erfolgswahrscheinlichkeit"
            return DecisionOutcome.REJECT, metadata
        else:
            metadata["reason"] = "Mittlere Erfolgswahrscheinlichkeit"
            return DecisionOutcome.HUMAN_REVIEW, metadata


# Test-Szenarien basierend auf dem QIMES-Dokument
def create_test_scenarios() -> List[EthicalScenario]:
    """
    Erstellt die Testszenarien aus dem QIMES-Framework
    """
    scenarios = [
        # Szenario 1: Medizinische Triage
        EthicalScenario(
            name="Medizinische Triage (jung vs. alt)",
            description="Ressourcen-Allokation: Jüngerer Patient mit höherer Überlebenschance vs. älterer Patient",
            harm_level=0.7,  # Hoher Schaden (jemand wird benachteiligt)
            benefit_level=0.6,  # Mittlerer Nutzen (statistische Effizienz)
            context_factors={"urgency": 0.9, "transparency": 0.8, "social_impact": 0.9},
            dignity_violations=["no_discrimination"],  # Altersdiskriminierung
            ground_truth="reject"  # Sollte abgelehnt werden
        ),
        
        # Szenario 2: Verdeckte Emotionsanalyse
        EthicalScenario(
            name="Heimliche Emotionsanalyse im Handel",
            description="KI analysiert Kundenemotionen ohne Wissen zur Verkaufsoptimierung",
            harm_level=0.8,  # Hoher Schaden (Manipulation, Privatsphäre)
            benefit_level=0.7,  # Hoher Nutzen (für Unternehmen)
            context_factors={"urgency": 0.2, "transparency": 0.0, "social_impact": 0.6},
            dignity_violations=["privacy_protection", "autonomy_respect", "transparency"],
            ground_truth="blocked"  # Sollte blockiert werden
        ),
        
        # Szenario 3: Kreditwürdigkeit mit Proxy-Variablen
        EthicalScenario(
            name="Kredit-Scoring mit Wohnort",
            description="Kreditablehnung basierend auf statistischer Korrelation mit Wohngebiet",
            harm_level=0.6,  # Mittlerer Schaden (mittelbare Diskriminierung)
            benefit_level=0.5,  # Mittlerer Nutzen (Risikominimierung)
            context_factors={"urgency": 0.4, "transparency": 0.5, "social_impact": 0.7},
            dignity_violations=["no_discrimination"],  # Diskriminierung nach Wohnort
            ground_truth="human_review"  # Sollte geprüft werden
        ),
        
        # Szenario 4: Legitime Gesundheitsüberwachung
        EthicalScenario(
            name="Freiwillige Gesundheits-App",
            description="Fitness-Tracker mit expliziter Einwilligung und transparenter Datennutzung",
            harm_level=0.2,  # Geringer Schaden (mit Einwilligung)
            benefit_level=0.8,  # Hoher Nutzen (Gesundheitsförderung)
            context_factors={"urgency": 0.3, "transparency": 0.9, "social_impact": 0.5},
            dignity_violations=[],  # Keine Verletzungen
            ground_truth="approve"  # Sollte genehmigt werden
        ),
        
        # Szenario 5: Pandemie-Tracking
        EthicalScenario(
            name="COVID-Kontaktverfolgung",
            description="Standort-Tracking zur Pandemiebekämpfung mit zeitlicher Begrenzung",
            harm_level=0.5,  # Mittlerer Schaden (Privatsphäre)
            benefit_level=0.9,  # Sehr hoher Nutzen (Leben retten)
            context_factors={"urgency": 1.0, "transparency": 0.7, "social_impact": 1.0},
            dignity_violations=[],  # Keine wenn transparent und befristet
            ground_truth="approve"  # Sollte genehmigt werden (mit Auflagen)
        ),
        
        # Szenario 6: Hiring-Algorithmus mit Gender-Bias
        EthicalScenario(
            name="KI-Recruiting mit historischem Bias",
            description="Recruiting-KI trainiert auf historische Daten benachteiligt Frauen",
            harm_level=0.9,  # Sehr hoher Schaden (systematische Diskriminierung)
            benefit_level=0.6,  # Mittlerer Nutzen (Effizienz)
            context_factors={"urgency": 0.3, "transparency": 0.4, "social_impact": 0.8},
            dignity_violations=["no_discrimination", "equal_treatment"],
            ground_truth="blocked"  # Sollte blockiert werden
        ),
        
        # Szenario 7: Personalisierte Bildung
        EthicalScenario(
            name="Adaptive Lernplattform",
            description="KI passt Lerninhalte individuell an, speichert Lernverhalten",
            harm_level=0.3,  # Geringer Schaden (Datenschutz mit Einwilligung)
            benefit_level=0.8,  # Hoher Nutzen (besseres Lernen)
            context_factors={"urgency": 0.4, "transparency": 0.8, "social_impact": 0.7},
            dignity_violations=[],  # Keine bei transparenter Nutzung
            ground_truth="approve"
        ),
        
        # Szenario 8: Social Credit System
        EthicalScenario(
            name="Soziales Scoring-System",
            description="Bewertung von Bürgern basierend auf Verhalten für Zugang zu Dienstleistungen",
            harm_level=0.95,  # Extremer Schaden (totale Überwachung)
            benefit_level=0.5,  # Fragwürdiger Nutzen (soziale Kontrolle)
            context_factors={"urgency": 0.2, "transparency": 0.3, "social_impact": 1.0},
            dignity_violations=["privacy_protection", "autonomy_respect", "dignity_as_subject"],
            ground_truth="blocked"  # Sollte blockiert werden
        )
    ]
    
    return scenarios


def run_comparison(scenarios: List[EthicalScenario]) -> Dict:
    """
    Führt alle Modelle auf allen Szenarien aus und vergleicht
    """
    models = [
        QIMESModel(),
        UtilitarianModel(),
        RuleBasedModel(),
        StatisticalModel()
    ]
    
    results = {model.name: [] for model in models}
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"Szenario: {scenario.name}")
        print(f"{'='*80}")
        
        for model in models:
            decision, metadata = model.decide(scenario)
            
            result = {
                "scenario": scenario.name,
                "decision": decision.value,
                "metadata": metadata,
                "ground_truth": scenario.ground_truth
            }
            
            results[model.name].append(result)
            
            print(f"\n{model.name}:")
            print(f"  Entscheidung: {decision.value}")
            print(f"  Begründung: {metadata.get('reason', 'N/A')}")
            
    return results


def evaluate_models(results: Dict) -> Dict:
    """
    Evaluiert die Modelle anhand verschiedener Metriken
    """
    evaluation = {}
    
    for model_name, decisions in results.items():
        # Mapping für Ground Truth Vergleich
        correct = 0
        total = 0
        
        dignity_blocks = 0
        human_reviews = 0
        
        for decision in decisions:
            total += 1
            ground_truth = decision["ground_truth"]
            actual = decision["decision"]
            
            # Vereinfachte Korrektheitsprüfung
            if ground_truth == "blocked" and actual == "blocked_by_dignity":
                correct += 1
            elif ground_truth == "human_review" and actual == "human_review":
                correct += 1
            elif ground_truth == "approve" and actual == "approve":
                correct += 1
            elif ground_truth == "reject" and actual == "reject":
                correct += 1
            
            if actual == "blocked_by_dignity":
                dignity_blocks += 1
            if actual == "human_review":
                human_reviews += 1
        
        evaluation[model_name] = {
            "accuracy": correct / total if total > 0 else 0,
            "dignity_blocks": dignity_blocks,
            "human_reviews": human_reviews,
            "total_decisions": total
        }
    
    return evaluation


if __name__ == "__main__":
    print("QIMES Framework - Vergleichstest")
    print("="*80)
    
    scenarios = create_test_scenarios()
    results = run_comparison(scenarios)
    
    print("\n\n" + "="*80)
    print("EVALUATION")
    print("="*80)
    
    evaluation = evaluate_models(results)
    
    for model_name, metrics in evaluation.items():
        print(f"\n{model_name}:")
        print(f"  Genauigkeit: {metrics['accuracy']*100:.1f}%")
        print(f"  Würde-Blocks: {metrics['dignity_blocks']}")
        print(f"  Human Reviews: {metrics['human_reviews']}")
    
    # Speichere Ergebnisse
    with open('/home/claude/qimes_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "results": results,
            "evaluation": evaluation
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nErgebnisse gespeichert in: /home/claude/qimes_results.json")
