from router.calibration import recalibrate_threshold, get_current_threshold


def main():
    print("=" * 60)
    print("SmartRoute-MCP — Threshold Recalibration")
    print("=" * 60)
 
    before = get_current_threshold()
    print(f"\nCurrent threshold: {before}")
    print("(Lower = pickier, more goes to the strong model, higher quality/cost)")
    print("(Higher = more trusting, more stays on the weak model, lower cost)\n")
 
    result = recalibrate_threshold(sample_limit=50, verbose=True)
 
    print("\n" + "-" * 60)
    if result["action"] == "no_change" and result["sample_size"] >= 20:
        print("No change needed - the system is performing within its "
              "healthy range.")
    elif result["action"] == "no_change":
        print("Not enough recent history to make a confident adjustment yet. "
              "Run test_router.py, test_agents.py, or use the app a bit more, "
              "then try again.")
    else:
        direction = "more selective (send more to the strong model)" \
            if result["action"] == "lowered" else \
            "more trusting (send more to the cheap model)"
        print(f"Adjusted! The system is now {direction}.")
    print("-" * 60)
 
 
if __name__ == "__main__":
    main()
