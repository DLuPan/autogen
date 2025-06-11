import pytest


@pytest.mark.agent
def test_investment_summary_report_agent():
    from autogenstudio.gallery.agents.investment_summary_report import InvestmentSummaryReportAgent

    # Create an instance of the InvestmentSummaryReportAgent
    agent = InvestmentSummaryReportAgent(
        name="InvestmentSummaryReportAgent",
        model_client="gpt-4o",
        description="An agent that generates investment summary reports.",
        system_message="You are an expert in generating investment summary reports.",
    )

    # Check if the agent is initialized correctly
    assert agent.name == "InvestmentSummaryReportAgent"
    assert agent.description == "An agent that generates investment summary reports."
    assert agent.system_message == "You are an expert in generating investment summary reports."
