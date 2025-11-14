import os
import configparser
import wx
from logging import info, warning, debug, error

class ConfigManager:
    """Manages configuration for JLC KiCad Library Loader"""
    
    CONFIG_FILENAME = "jlc-kicad-lib-loader.ini"
    
    def __init__(self, kiprjmod):
        self.kiprjmod = kiprjmod
        self.config_path = os.path.join(kiprjmod, self.CONFIG_FILENAME)
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from INI file"""
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
                debug(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                warning(f"Failed to load configuration: {e}")
        else:
            debug(f"Configuration file not found at {self.config_path}")
    
    def save_config(self):
        """Save configuration to INI file"""
        try:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            debug(f"Saved configuration to {self.config_path}")
        except Exception as e:
            error(f"Failed to save configuration: {e}")
    
    def get_library_name(self, default="EasyEDA_Lib"):
        """Get the library name from config"""
        if not self.config.has_section('Library'):
            return default
        return self.config.get('Library', 'name', fallback=default)
    
    def set_library_name(self, name):
        """Set the library name in config"""
        if not self.config.has_section('Library'):
            self.config.add_section('Library')
        self.config.set('Library', 'name', name)
        self.save_config()


class LibraryTableManager:
    """Manages KiCad symbol and footprint library tables"""
    
    def __init__(self, kiprjmod):
        self.kiprjmod = kiprjmod
        self.sym_lib_table_path = os.path.join(kiprjmod, "sym-lib-table")
        self.fp_lib_table_path = os.path.join(kiprjmod, "fp-lib-table")
    
    def check_library_exists(self, lib_name, lib_type="symbol"):
        """Check if a library exists in the library table
        
        Args:
            lib_name: Name of the library
            lib_type: Either "symbol" or "footprint"
        
        Returns:
            True if library exists, False otherwise
        """
        table_path = self.sym_lib_table_path if lib_type == "symbol" else self.fp_lib_table_path
        
        if not os.path.exists(table_path):
            debug(f"{lib_type} library table not found at {table_path}")
            return False
        
        try:
            with open(table_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check if library name exists in the table
                # Library entries look like: (lib (name "LibraryName")...)
                return f'(name "{lib_name}")' in content
        except Exception as e:
            warning(f"Failed to read {lib_type} library table: {e}")
            return False
    
    def add_library_to_table(self, lib_name, lib_path, lib_type="symbol"):
        """Add a library to the library table
        
        Args:
            lib_name: Name of the library
            lib_path: Path to the library file (relative to project)
            lib_type: Either "symbol" or "footprint"
        
        Returns:
            True if successful, False otherwise
        """
        table_path = self.sym_lib_table_path if lib_type == "symbol" else self.fp_lib_table_path
        
        # Determine the library entry format for EasyEDA library
        # Both symbol and footprint libraries use the same .elibz file
        if lib_type == "symbol":
            lib_entry = f'  (lib (name "{lib_name}")(type "EasyEDA (JLCEDA) Pro")(uri "${{KIPRJMOD}}/{lib_name}/{lib_name}.elibz")(options "")(descr ""))\n'
        else:
            lib_entry = f'  (lib (name "{lib_name}")(type "EasyEDA / JLCEDA Pro")(uri "${{KIPRJMOD}}/{lib_name}/{lib_name}.elibz")(options "")(descr ""))\n'
        
        try:
            # Create table if it doesn't exist
            if not os.path.exists(table_path):
                table_content = f"(sym_lib_table\n{lib_entry})\n" if lib_type == "symbol" else f"(fp_lib_table\n{lib_entry})\n"
                with open(table_path, 'w', encoding='utf-8') as f:
                    f.write(table_content)
                info(f"Created new {lib_type} library table with {lib_name}")
                return True
            
            # Read existing table
            with open(table_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the position to insert (before the closing parenthesis)
            insert_pos = -1
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == ')':
                    insert_pos = i
                    break
            
            if insert_pos == -1:
                error(f"Invalid {lib_type} library table format")
                return False
            
            # Insert the new library entry
            lines.insert(insert_pos, lib_entry)
            
            # Write back to file
            with open(table_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            info(f"Added {lib_name} to {lib_type} library table")
            return True
            
        except Exception as e:
            error(f"Failed to add library to {lib_type} table: {e}")
            return False
    
    def prompt_add_library(self, parent, lib_name, lib_path):
        """Prompt user to add library to symbol and footprint tables
        
        Args:
            parent: Parent window for the dialog
            lib_name: Name of the library
            lib_path: Path to the library
        
        Returns:
            True if libraries were added or already exist, False if user cancelled
        """
        symbol_exists = self.check_library_exists(lib_name, "symbol")
        footprint_exists = self.check_library_exists(lib_name, "footprint")
        
        if symbol_exists and footprint_exists:
            debug(f"Library {lib_name} already exists in both tables")
            return True
        
        # Build message
        missing_libs = []
        if not symbol_exists:
            missing_libs.append("Symbol")
        if not footprint_exists:
            missing_libs.append("Footprint")
        
        msg = f"The library '{lib_name}' is not found in the project-specific {' and '.join(missing_libs)} library table(s).\n\n"
        msg += "Would you like to add it automatically?"
        
        dlg = wx.MessageDialog(
            parent,
            msg,
            "Add Library to Project",
            wx.YES_NO | wx.ICON_QUESTION | wx.YES_DEFAULT
        )
        
        result = dlg.ShowModal()
        dlg.Destroy()
        
        if result == wx.ID_YES:
            success = True
            
            if not symbol_exists:
                if not self.add_library_to_table(lib_name, lib_path, "symbol"):
                    success = False
            
            if not footprint_exists:
                if not self.add_library_to_table(lib_name, lib_path, "footprint"):
                    success = False
            
            if success:
                info_dlg = wx.MessageDialog(
                    parent,
                    f"Library '{lib_name}' has been added to the project library tables.\n\n"
                    "Note: You may need to restart KiCad for the changes to take effect.",
                    "Library Added Successfully",
                    wx.OK | wx.ICON_INFORMATION
                )
                info_dlg.ShowModal()
                info_dlg.Destroy()
            
            return success
        
        return False
