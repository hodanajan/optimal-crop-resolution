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
                "use_5_12": ("BOOLEAN", {"default": True}),    # 640 x 1536
                "use_4_7": ("BOOLEAN", {"default": True}),     # 768 x 1344
                "use_13_19": ("BOOLEAN", {"default": True}),   # 832 x 1216
                "use_7_9": ("BOOLEAN", {"default": True}),     # 896 x 1152
                "use_1_1": ("BOOLEAN", {"default": True}),     # 1024 x 1024
                "use_9_7": ("BOOLEAN", {"default": True}),     # 1152 x 896
                "use_19_13": ("BOOLEAN", {"default": True}),   # 1216 x 832
                "use_7_4": ("BOOLEAN", {"default": True}),     # 1344 x 768
                "use_12_5": ("BOOLEAN", {"default": True}),    # 1536 x 640
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
            "use_5_12": (5, 12),    # 640 x 1536
            "use_4_7": (4, 7),      # 768 x 1344
            "use_13_19": (13, 19),  # 832 x 1216
            "use_7_9": (7, 9),      # 896 x 1152
            "use_1_1": (1, 1),      # 1024 x 1024
            "use_9_7": (9, 7),      # 1152 x 896
            "use_19_13": (19, 13),  # 1216 x 832
            "use_7_4": (7, 4),      # 1344 x 768
            "use_12_5": (12, 5),    # 1536 x 640
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

    def calculate(self, width, height, force_aspect_ratio_width=-1, force_aspect_ratio_height=-1, custom_ratios="", **kwargs):
        """Calculate the optimal crop resolution based on nearest aspect ratio or forced ratio"""
        current_ratio = width / height
        
        # If forced aspect ratio is provided, use it
        if force_aspect_ratio_width > 0 and force_aspect_ratio_height > 0:
            closest_ratio = (force_aspect_ratio_width, force_aspect_ratio_height)
            closest_ratio_float = force_aspect_ratio_width / force_aspect_ratio_height
            
            # Calculate new dimensions that maintain maximum area
            if current_ratio > closest_ratio_float:
                new_width = int(height * closest_ratio_float)
                new_height = height
            else:
                new_width = width
                new_height = int(width / closest_ratio_float)
            
            return (new_width, new_height, closest_ratio[0], closest_ratio[1])
        
        # Otherwise use enabled ratios
        enabled_ratios = self.get_enabled_ratios(custom_ratios, **kwargs)
        if not enabled_ratios:
            # If no ratios selected, return original dimensions and 1:1
            return (width, height, 1, 1)
        
        # Convert ratios to floats for comparison
        ratio_values = [(ratio, ratio[0] / ratio[1]) for ratio in enabled_ratios]
        
        # Find closest ratio
        differences = [abs(current_ratio - ratio_float) for _, ratio_float in ratio_values]
        closest_ratio = enabled_ratios[differences.index(min(differences))]
        closest_ratio_float = closest_ratio[0] / closest_ratio[1]
        
        # Calculate new dimensions that maintain maximum area
        if current_ratio > closest_ratio_float:
            new_width = int(height * closest_ratio_float)
            new_height = height
        else:
            new_width = width
            new_height = int(width / closest_ratio_float)
        
        return (new_width, new_height, closest_ratio[0], closest_ratio[1])

# This part is required to register the node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "AspectRatioCalculator": AspectRatioCalculatorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioCalculator": "Aspect Ratio Calculator"
}
