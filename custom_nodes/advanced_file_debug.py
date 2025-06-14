from langflow.custom import Component
from langflow.io import FileInput, Output
from langflow.schema import Message
import os


class AdvancedFileDebugComponent(Component):
    display_name = "Advanced File Debug"
    description = "Advanced debug component to find original filename"
    icon = "search"
    name = "AdvancedFileDebug"

    inputs = [
        FileInput(
            name="debug_file",
            display_name="Debug File",
            info="Upload any file to debug and find original filename",
            file_types=["rtf", "txt", "pdf", "doc", "docx"],
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Debug Results", name="debug_results", method="advanced_debug"),
    ]

    def advanced_debug(self) -> Message:
        try:
            # Get the uploaded file path
            file_path = self.debug_file
            
            debug_info = []
            debug_info.append("=== ADVANCED FILE DEBUG COMPONENT ===")
            debug_info.append(f"File path received: {file_path}")
            debug_info.append(f"File basename: {os.path.basename(file_path)}")
            debug_info.append("")
            
            # Test 1: ALL attributes on self (exhaustive search)
            debug_info.append("Test 1 - ALL attributes on self:")
            all_attrs = [attr for attr in dir(self) if not attr.startswith('__')]
            for attr_name in all_attrs:
                try:
                    attr_value = getattr(self, attr_name)
                    if isinstance(attr_value, str) and ('gmbh' in attr_value.lower() or 'rtf' in attr_value.lower() or len(attr_value) < 200):
                        debug_info.append(f"  self.{attr_name} = {attr_value}")
                except:
                    pass
            debug_info.append("")
            
            # Test 2: _attributes dictionary (complete dump)
            debug_info.append("Test 2 - _attributes dictionary (COMPLETE):")
            if hasattr(self, '_attributes'):
                debug_info.append(f"  _attributes keys: {list(self._attributes.keys())}")
                for key, value in self._attributes.items():
                    debug_info.append(f"  _attributes['{key}'] = {value}")
            debug_info.append("")
            
            # Test 3: _inputs dictionary (DEEP inspection)
            debug_info.append("Test 3 - _inputs dictionary (DEEP):")
            if hasattr(self, '_inputs'):
                debug_info.append(f"  _inputs keys: {list(self._inputs.keys())}")
                if 'debug_file' in self._inputs:
                    debug_input = self._inputs['debug_file']
                    debug_info.append(f"  debug_input object: {debug_input}")
                    debug_info.append(f"  debug_input type: {type(debug_input)}")
                    
                    # Check ALL attributes (not just specific ones)
                    all_input_attrs = [attr for attr in dir(debug_input) if not attr.startswith('_')]
                    debug_info.append(f"  debug_input ALL attributes: {all_input_attrs}")
                    
                    # Get values for ALL attributes
                    for attr in all_input_attrs:
                        try:
                            attr_value = getattr(debug_input, attr)
                            if not callable(attr_value):  # Skip methods
                                debug_info.append(f"  debug_input.{attr} = {attr_value}")
                        except Exception as e:
                            debug_info.append(f"  debug_input.{attr} = ERROR: {e}")
                            
                    # Check private attributes too
                    private_attrs = [attr for attr in dir(debug_input) if attr.startswith('_') and not attr.startswith('__')]
                    debug_info.append(f"  debug_input PRIVATE attributes: {private_attrs}")
                    for attr in private_attrs:
                        try:
                            attr_value = getattr(debug_input, attr)
                            if not callable(attr_value) and isinstance(attr_value, (str, dict, list)):
                                debug_info.append(f"  debug_input.{attr} = {attr_value}")
                        except:
                            pass
            debug_info.append("")
            
            # Test 4: inputs class definition (DEEP)
            debug_info.append("Test 4 - inputs class definition (DEEP):")
            for i, input_def in enumerate(self.inputs):
                if input_def.name == "debug_file":
                    debug_info.append(f"  Input {i}: {input_def}")
                    debug_info.append(f"  Input {i} type: {type(input_def)}")
                    
                    # Check ALL attributes
                    all_def_attrs = [attr for attr in dir(input_def) if not attr.startswith('_')]
                    debug_info.append(f"  Input {i} ALL attributes: {all_def_attrs}")
                    
                    # Get values for ALL attributes
                    for attr in all_def_attrs:
                        try:
                            attr_value = getattr(input_def, attr)
                            if not callable(attr_value):  # Skip methods
                                debug_info.append(f"  input_def.{attr} = {attr_value}")
                        except Exception as e:
                            debug_info.append(f"  input_def.{attr} = ERROR: {e}")
            debug_info.append("")
            
            # Test 5: Check vertex and graph properties
            debug_info.append("Test 5 - Vertex and Graph properties:")
            if hasattr(self, '_vertex'):
                debug_info.append(f"  _vertex: {self._vertex}")
                if hasattr(self._vertex, 'data'):
                    debug_info.append(f"  _vertex.data: {self._vertex.data}")
                    # Deep dive into vertex data
                    try:
                        vertex_data = self._vertex.data
                        if hasattr(vertex_data, '__dict__'):
                            for attr in dir(vertex_data):
                                if not attr.startswith('_'):
                                    try:
                                        val = getattr(vertex_data, attr)
                                        if not callable(val):
                                            debug_info.append(f"  _vertex.data.{attr} = {val}")
                                    except:
                                        pass
                    except:
                        pass
                if hasattr(self._vertex, 'params'):
                    debug_info.append(f"  _vertex.params: {self._vertex.params}")
            if hasattr(self, 'graph'):
                debug_info.append(f"  graph: {self.graph}")
            debug_info.append("")
            
            # Test 6: Search for any string containing the target filename
            debug_info.append("Test 6 - Search for 'gmbh' or original filename:")
            target_strings = []
            
            def search_object(obj, path="", depth=0):
                if depth > 5:  # Prevent infinite recursion
                    return
                try:
                    if isinstance(obj, str):
                        if 'gmbh' in obj.lower() or (obj.endswith('.RTF') and len(obj) < 100):
                            target_strings.append(f"{path}: {obj}")
                    elif isinstance(obj, dict):
                        for key, value in obj.items():
                            search_object(value, f"{path}.{key}", depth + 1)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            search_object(item, f"{path}[{i}]", depth + 1)
                    elif hasattr(obj, '__dict__'):
                        for attr_name in dir(obj):
                            if not attr_name.startswith('__'):
                                try:
                                    attr_value = getattr(obj, attr_name)
                                    if not callable(attr_value):
                                        search_object(attr_value, f"{path}.{attr_name}", depth + 1)
                                except:
                                    pass
                except:
                    pass
            
            search_object(self, "self")
            
            for target in target_strings:
                debug_info.append(f"  FOUND: {target}")
            
            if not target_strings:
                debug_info.append("  No target strings found")
            
            debug_info.append("")
            debug_info.append("=== END ADVANCED FILE DEBUG ===")
            
            # Join all debug info
            final_text = "\n".join(debug_info)
            
            self.status = f"Advanced debug completed for: {os.path.basename(file_path)}"
            
            return Message(
                text=final_text,
                sender="Advanced File Debug",
                sender_name="Advanced File Debug Component"
            )
            
        except Exception as e:
            error_msg = f"Error in advanced file debug: {str(e)}"
            self.status = error_msg
            return Message(
                text=error_msg,
                sender="Advanced File Debug",
                sender_name="Advanced File Debug Component"
            )
