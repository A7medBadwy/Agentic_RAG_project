import ast
import operator
import re

_ALLOWED_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos, ast.Mod: operator.mod,
}

def safe_calculate(expression: str):
    tree = ast.parse(expression, mode="eval")
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](visit(node.operand))
        raise ValueError("Unsupported or unsafe mathematical expression")
    result = visit(tree)
    if abs(result) > 1e100:
        raise ValueError("Result is outside the supported range")
    return result

class AnalystAgent:
    def analyze(self, question: str, evidence: list[dict]) -> dict:
        text = "\n".join(x.get("text", "") for x in evidence)
        # Conservative evidence check: require at least one meaningful retrieved passage.
        sufficient = bool(evidence) and max((len(x.get("text", "")) for x in evidence), default=0) >= 40
        analysis = {
            "sufficient_evidence": sufficient,
            "evidence_count": len(evidence),
            "document_names": sorted({x.get("document_name", "Unknown") for x in evidence}),
            "calculation": None,
            "comparison": None,
            "notes": "Evidence sufficiency is a heuristic and should be evaluated for your dataset."
        }
        # Only execute an explicit arithmetic expression supplied by the user.
        match = re.search(r"(?:calculate|compute)\s+([0-9.() +*/%\-]+)", question, re.I)
        if match:
            try:
                analysis["calculation"] = {
                    "expression": match.group(1).strip(),
                    "result": safe_calculate(match.group(1).strip())
                }
            except Exception as exc:
                analysis["calculation"] = {"error": str(exc)}
        if re.search(r"compare|difference|versus|vs\b", question, re.I):
            analysis["comparison"] = "Comparison requested; findings are grounded in the retrieved passages."
        return analysis
