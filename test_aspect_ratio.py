from aspect_ratio_calculator import AspectRatioCalculatorNode

def calculate_pixel_loss(original_width, original_height, new_width, new_height):
    original_pixels = original_width * original_height
    new_pixels = new_width * new_height
    return original_pixels - new_pixels

def test_comprehensive():
    calculator = AspectRatioCalculatorNode()
    
    test_cases = [
        # Edge cases
        (1, 1),           # Square minimum
        (8192, 8192),     # Square maximum
        (8192, 1),        # Extreme landscape
        (1, 8192),        # Extreme portrait
        
        # Common resolutions
        (1920, 1080),     # FHD
        (3840, 2160),     # 4K
        (1440, 2560),     # Phone screen
        
        # Prime numbers (potentially tricky for division)
        (997, 751),
        (1999, 1777),
        
        # Odd numbers
        (901, 601),
        (1501, 999),
        (899, 590),
        
        # Numbers close to common ratios
        (1024, 768),      # Exactly 4:3
        (1025, 768),      # Slightly off 4:3
        (1024, 769),      # Slightly off 4:3
    ]
    
    print("Comprehensive Test Results:")
    print("-" * 120)
    print(f"{'Input':<20} {'Output':<20} {'Ratio':<10} {'Width Units':<15} {'Height Units':<15} {'Pixels Lost %':<15} {'Valid?':<10}")
    print("-" * 120)
    
    for width, height in test_cases:
        # Test with all ratios enabled
        new_width, new_height, ratio_w, ratio_h = calculator.calculate(
            width, height,
            use_1_1=True, use_2_3=True, use_3_2=True,
            use_4_3=True, use_3_4=True, use_16_9=True,
            use_9_16=True
        )
        
        # Verify results
        width_units = new_width / ratio_w
        height_units = new_height / ratio_h
        
        # Check if results are valid
        is_valid = all([
            width_units.is_integer(),           # Width divides evenly by ratio_w
            height_units.is_integer(),          # Height divides evenly by ratio_h
            abs(width_units - height_units) < 0.001,  # Both dimensions use same unit size
            new_width <= width,                 # New width doesn't exceed original
            new_height <= height,               # New height doesn't exceed original
            new_width > 0,                      # Positive width
            new_height > 0,                     # Positive height
        ])
        
        # Calculate pixel loss percentage
        pixels_lost = calculate_pixel_loss(width, height, new_width, new_height)
        original_pixels = width * height
        loss_percentage = (pixels_lost / original_pixels) * 100
        
        print(f"{f'{width}x{height}':<20} {f'{new_width}x{new_height}':<20} "
              f"{f'{ratio_w}:{ratio_h}':<10} {f'{width_units:.2f}':<15} "
              f"{f'{height_units:.2f}':<15} {f'{loss_percentage:.1f}%':<15} {'✓' if is_valid else '✗':<10}")
        
        if not is_valid:
            print(f"FAILED for {width}x{height}:")
            print(f"- Width units integer: {width_units.is_integer()}")
            print(f"- Height units integer: {height_units.is_integer()}")
            print(f"- Units match: {abs(width_units - height_units) < 0.001}")
            print(f"- Width in bounds: {new_width <= width}")
            print(f"- Height in bounds: {new_height <= height}")
            print(f"- Positive dimensions: {new_width > 0 and new_height > 0}")
            print(f"- Pixels lost: {pixels_lost:,} ({loss_percentage:.1f}%)")
            print()

test_comprehensive()