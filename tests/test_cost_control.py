import unittest
from types import SimpleNamespace
from cost_control import UsageLedger

class FakeResponse:
    usage = SimpleNamespace(input_tokens=2000,output_tokens=1000,
                            input_tokens_details=SimpleNamespace(cached_tokens=500))
    def model_dump(self,mode="json"):
        return {"output":[{"type":"web_search_call"}]}

class CostControlTests(unittest.TestCase):
    def test_quote_and_budget(self):
        x=UsageLedger(budget=.001)
        with self.assertRaises(ValueError): x.preflight("gpt-6.1-terra",2000,4000)
    def test_unknown_model_fails_closed(self):
        with self.assertRaises(ValueError): UsageLedger().quote("unknown",100,200)
    def test_record(self):
        x=UsageLedger()
        row=x.record("gpt-6.1-terra","Researcher",FakeResponse(),True)
        self.assertEqual(row["web_search_calls"],1)
        self.assertEqual(row["input_tokens"],2000)
        self.assertGreater(x.total,.02)
if __name__=="__main__": unittest.main()
