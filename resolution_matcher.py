"""
Resolution Matcher node for ComfyUI
Selects the closest predefined resolution that matches the input aspect ratio
"""

class ResolutionMatcherNode:
    """Node that matches input resolution to the closest predefined resolution with the same aspect ratio"""
    
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
                # SD1.5 resolutions
                "use_sd15_1:1_512x512": ("BOOLEAN", {"default": False}),    # 512x512
                "use_sd1.5/sdxl_1:1_768x768": ("BOOLEAN", {"default": False}),    # 768x768 (works for both SD1.5 and SDXL)
                "use_sd15_3:2_768x512": ("BOOLEAN", {"default": False}),    # 768x512
                "use_sd15_2:3_512x768": ("BOOLEAN", {"default": False}),    # 512x768
                "use_sd15_4:3_768x576": ("BOOLEAN", {"default": False}),    # 768x576
                "use_sd15_3:4_576x768": ("BOOLEAN", {"default": False}),    # 576x768
                "use_sd15_16:9_912x512": ("BOOLEAN", {"default": False}),   # 912x512
                "use_sd15_9:16_512x912": ("BOOLEAN", {"default": False}),   # 512x912
                
                # SDXL resolutions
                "use_sdxl_1:1_1024x1024": ("BOOLEAN", {"default": False}),  # 1024x1024
                "use_sdxl_3:2_1152x768": ("BOOLEAN", {"default": False}),   # 1152x768
                "use_sdxl_2:3_768x1152": ("BOOLEAN", {"default": False}),   # 768x1152
                "use_sdxl_4:3_1152x864": ("BOOLEAN", {"default": False}),   # 1152x864
                "use_sdxl_3:4_864x1152": ("BOOLEAN", {"default": False}),   # 864x1152
                "use_sdxl_16:9_1360x768": ("BOOLEAN", {"default": False}),  # 1360x768
                "use_sdxl_9:16_768x1360": ("BOOLEAN", {"default": False}),  # 768x1360
                
                # Flux resolutions
                "use_flux_1:1_1408x1408": ("BOOLEAN", {"default": False}),  # 1408x1408
                "use_flux_3:2_1728x1152": ("BOOLEAN", {"default": False}),  # 1728x1152
                "use_flux_4:3_1664x1216": ("BOOLEAN", {"default": False}),  # 1664x1216
                "use_flux_16:9_1920x1088": ("BOOLEAN", {"default": False}), # 1920x1088
                "use_flux_21:9_2176x960": ("BOOLEAN", {"default": False}),  # 2176x960
                
                "custom_resolutions": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Optional: 1920x1080,1280x720,etc"
                }),
            }
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "match_resolution"
    CATEGORY = "image/resolution"

    def __init__(self):
        # Resolution presets organized by model
        self.resolutions = {
            # SD1.5 resolutions
            "use_sd15_1:1_512x512": (512, 512),
            "use_sd1.5/sdxl_1:1_768x768": (768, 768),  # Works for both SD1.5 and SDXL
            "use_sd15_3:2_768x512": (768, 512),
            "use_sd15_2:3_512x768": (512, 768),
            "use_sd15_4:3_768x576": (768, 576),
            "use_sd15_3:4_576x768": (576, 768),
            "use_sd15_16:9_912x512": (912, 512),
            "use_sd15_9:16_512x912": (512, 912),
            
            # SDXL resolutions
            "use_sdxl_1:1_1024x1024": (1024, 1024),
            "use_sdxl_3:2_1152x768": (1152, 768),
            "use_sdxl_2:3_768x1152": (768, 1152),
            "use_sdxl_4:3_1152x864": (1152, 864),
            "use_sdxl_3:4_864x1152": (864, 1152),
            "use_sdxl_16:9_1360x768": (1360, 768),
            "use_sdxl_9:16_768x1360": (768, 1360),
            
            # Flux resolutions
            "use_flux_1:1_1408x1408": (1408, 1408),
            "use_flux_3:2_1728x1152": (1728, 1152),
            "use_flux_4:3_1664x1216": (1664, 1216),
            "use_flux_16:9_1920x1088": (1920, 1088),
            "use_flux_21:9_2176x960": (2176, 960),
        }

    def parse_custom_resolutions(self, custom_resolutions_str):
        """Parse custom resolutions string into list of tuples"""
        if not custom_resolutions_str.strip():
            return []
            
        try:
            resolutions = []
            for res in custom_resolutions_str.split(','):
                if 'x' not in res:
                    continue
                w, h = map(int, res.strip().split('x'))
                if w > 0 and h > 0:  # Validate positive numbers
                    resolutions.append((w, h))
            return resolutions
        except (ValueError, TypeError):
            print(f"Warning: Invalid custom resolution format: {custom_resolutions_str}")
            return []

    def get_enabled_resolutions(self, custom_resolutions, **kwargs):
        """Get list of enabled resolutions based on checkbox inputs and custom resolutions"""
        enabled = [res for key, res in self.resolutions.items() 
                  if kwargs.get(key, False)]
        
        # Add custom resolutions
        custom = self.parse_custom_resolutions(custom_resolutions)
        return enabled + custom

    def match_resolution(self, width, height, custom_resolutions="", **kwargs):
        """Match input resolution to the closest predefined resolution with same aspect ratio"""
        
        def calculate_aspect_ratio(w, h):
            """Calculate reduced aspect ratio"""
            from math import gcd
            d = gcd(w, h)
            return (w // d, h // d)
        
        def calculate_pixel_difference(w1, h1, w2, h2):
            """Calculate percentage difference in total pixels"""
            pixels1 = w1 * h1
            pixels2 = w2 * h2
            return abs(pixels2 - pixels1) / pixels1 * 100

        # Get input aspect ratio
        input_ratio = calculate_aspect_ratio(width, height)
        input_pixels = width * height

        # Get enabled resolutions
        enabled_resolutions = self.get_enabled_resolutions(custom_resolutions, **kwargs)
        if not enabled_resolutions:
            return (width, height)

        # Find resolutions with matching aspect ratio
        matching_resolutions = []
        for res_w, res_h in enabled_resolutions:
            if calculate_aspect_ratio(res_w, res_h) == input_ratio:
                pixel_diff = calculate_pixel_difference(width, height, res_w, res_h)
                matching_resolutions.append((res_w, res_h, pixel_diff))

        # If no matching aspect ratios found, return original resolution
        if not matching_resolutions:
            return (width, height)

        # Sort by pixel difference and prefer larger resolutions when difference is similar
        matching_resolutions.sort(key=lambda x: (x[2], -(x[0] * x[1])))
        
        # Return the best match
        return (matching_resolutions[0][0], matching_resolutions[0][1])

# Register the node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "ResolutionMatcher": ResolutionMatcherNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionMatcher": "Resolution Matcher"
}
