"""
Aspect Ratio Calculator node for ComfyUI
Finds the optimal crop dimensions to match the nearest aspect ratio or uses a specified one
"""

class AspectRatioCalculatorNode:
    """Node that calculates the optimal crop resolution to match the nearest aspect ratio"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 8192
                }),
                "height": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 8192
                }),
            },
            "optional": {
                "use_1_1": ("BOOLEAN", {"default": True}),     # 1024 x 1024
                "use_2_3": ("BOOLEAN", {"default": True}),     # 683 x 1024
                "use_3_2": ("BOOLEAN", {"default": True}),     # 1024 x 683
                "use_4_3": ("BOOLEAN", {"default": True}),     # 1024 x 768
                "use_3_4": ("BOOLEAN", {"default": True}),     # 768 x 1024
                "use_16_9": ("BOOLEAN", {"default": True}),    # 1024 x 576
                "use_9_16": ("BOOLEAN", {"default": True}),    # 576 x 1024
                "custom_ratios": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Optional: 21:9,32:9,etc"
                }),
                "force_aspect_ratio_width": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 8192,
                }),
                "force_aspect_ratio_height": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 8192,
                }),
            }
        }
    
    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "aspect_ratio_width", "aspect_ratio_height")
    FUNCTION = "calculate"
    CATEGORY = "image/resolution"

    def __init__(self):
        self.ratios = {
            "use_1_1": (1, 1),      # 1024 x 1024
            "use_2_3": (2, 3),      # 683 x 1024
            "use_3_2": (3, 2),      # 1024 x 683
            "use_4_3": (4, 3),      # 1024 x 768
            "use_3_4": (3, 4),      # 768 x 1024
            "use_16_9": (16, 9),    # 1024 x 576
            "use_9_16": (9, 16),    # 576 x 1024
        }

    def parse_custom_ratios(self, custom_ratios_str):
        """Parse custom ratios string into list of tuples"""
        if not custom_ratios_str.strip():
            return []
            
        try:
            ratios = []
            for ratio in custom_ratios_str.split(','):
                if ':' not in ratio:
                    continue
                w, h = map(int, ratio.strip().split(':'))
                if w > 0 and h > 0:  # Validate positive numbers
                    ratios.append((w, h))
            return ratios
        except (ValueError, TypeError):
            print(f"Warning: Invalid custom ratio format: {custom_ratios_str}")
            return []

    def get_enabled_ratios(self, custom_ratios, **kwargs):
        """Get list of enabled ratios based on checkbox inputs and custom ratios"""
        enabled = [ratio for key, ratio in self.ratios.items() 
                  if kwargs.get(key, False)]
        
        # Add custom ratios
        custom = self.parse_custom_ratios(custom_ratios)
        return enabled + custom

    def calculate(self, width, height, force_aspect_ratio_width=-1, force_aspect_ratio_height=-1, 
                 custom_ratios="", **kwargs):
        """Calculate the optimal crop resolution based on nearest aspect ratio or forced ratio"""
        
        def calculate_dimensions_for_ratio(w, h, ratio_w, ratio_h):
            """Calculate dimensions and pixel loss for a given ratio"""
            current_r = w / h
            target_r = ratio_w / ratio_h
            
            if current_r > target_r:
                height_units = h // ratio_h
                new_height = height_units * ratio_h
                new_width = height_units * ratio_w
                
                if new_width > w:
                    width_units = w // ratio_w
                    new_width = width_units * ratio_w
                    new_height = width_units * ratio_h
            else:
                width_units = w // ratio_w
                new_width = width_units * ratio_w
                new_height = width_units * ratio_h
                
                if new_height > h:
                    height_units = h // ratio_h
                    new_height = height_units * ratio_h
                    new_width = height_units * ratio_w
            
            pixel_loss = (w * h) - (new_width * new_height)
            return new_width, new_height, pixel_loss
        
        # If forced aspect ratio is provided
        if force_aspect_ratio_width > 0 and force_aspect_ratio_height > 0:
            new_width, new_height, _ = calculate_dimensions_for_ratio(
                width, height, force_aspect_ratio_width, force_aspect_ratio_height
            )
            return (new_width, new_height, force_aspect_ratio_width, force_aspect_ratio_height)
        
        # Get enabled ratios
        enabled_ratios = self.get_enabled_ratios(custom_ratios, **kwargs)
        if not enabled_ratios:
            return (width, height, 1, 1)
        
        # Calculate dimensions and pixel loss for each ratio
        results = []
        for ratio in enabled_ratios:
            new_w, new_h, loss = calculate_dimensions_for_ratio(width, height, ratio[0], ratio[1])
            results.append((new_w, new_h, ratio[0], ratio[1], loss))
        
        # Choose ratio with minimum pixel loss
        results.sort(key=lambda x: x[4])  # Sort by pixel loss
        best_result = results[0]
        
        return (best_result[0], best_result[1], best_result[2], best_result[3])

# This part is required to register the node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "AspectRatioCalculator": AspectRatioCalculatorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioCalculator": "Aspect Ratio Calculator"
}
