# Payload Components

This directory contains React components for building and managing JSON payload templates for IoT devices.

## Components

### PayloadBuilder
The main visual JSON builder component with drag-and-drop functionality.

**Props:**
- `schema` - The JSON schema object with fields array
- `onChange` - Callback when schema changes
- `className` - Additional CSS classes

**Features:**
- Drag-and-drop field reordering
- Add/edit/delete fields
- Real-time preview
- Field type validation

### FieldEditor
Modal component for editing individual JSON fields.

**Props:**
- `field` - Field object to edit (null for new field)
- `onSave` - Callback when field is saved
- `onCancel` - Callback when editing is cancelled
- `existingFieldNames` - Array of existing field names for validation

**Supported Field Types:**
- **String**: Fixed value, random choice, random string
- **Number**: Fixed value, random integer, random float
- **Boolean**: Fixed value, random boolean
- **UUID**: Auto-generated UUID
- **Timestamp**: Current timestamp

### PayloadPreview
Component that shows a live preview of the generated JSON payload.

**Props:**
- `schema` - The JSON schema to preview
- `className` - Additional CSS classes

**Features:**
- Syntax-highlighted JSON display
- Refresh button to generate new sample
- Copy to clipboard functionality
- Field summary display

### PayloadList
Table component for displaying and managing payload templates.

**Props:**
- `payloads` - Array of payload objects
- `onAdd` - Callback for adding new payload
- `onEdit` - Callback for editing payload
- `onDelete` - Callback for deleting payload
- `onDuplicate` - Callback for duplicating payload
- `loading` - Loading state boolean

**Features:**
- Search and filter functionality
- Type-based filtering (Visual/Python)
- Sortable columns
- Action buttons for each payload

### PayloadForm
Form component for creating and editing payload templates.

**Props:**
- `payload` - Payload object to edit (null for new)
- `onSave` - Callback when payload is saved
- `onCancel` - Callback when form is cancelled

**Features:**
- Support for both visual and Python payload types
- Form validation
- Integrated PayloadBuilder for visual payloads
- Advanced Python code editor with Monaco Editor

### PythonCodeEditor
Advanced Python code editor with syntax highlighting and validation.

**Props:**
- `code` - Python code string
- `onChange` - Callback when code changes
- `onValidate` - Callback when validation completes
- `className` - Additional CSS classes
- `height` - Editor height (default: "400px")
- `showPreview` - Show preview panel (default: true)
- `deviceMetadata` - Mock device metadata for preview

**Features:**
- Monaco Editor with Python syntax highlighting
- Real-time code validation and error detection
- Auto-completion for IoT-specific functions
- Security validation (dangerous imports/functions)
- Live preview with mock execution
- Copy to clipboard functionality
- Integrated help documentation

## Usage Example

```jsx
import { PayloadBuilder, PayloadPreview } from '../components/payloads';

const MyComponent = () => {
  const [schema, setSchema] = useState({
    fields: [
      {
        name: 'temperature',
        type: 'number',
        generator: {
          type: 'random_float',
          min: 18.0,
          max: 25.0,
          decimals: 1
        }
      }
    ]
  });

  return (
    <div className="grid grid-cols-2 gap-6">
      <PayloadBuilder 
        schema={schema} 
        onChange={setSchema} 
      />
      <PayloadPreview 
        schema={schema} 
      />
    </div>
  );
};
```

## Schema Format

The JSON schema format used by these components:

```javascript
{
  fields: [
    {
      name: "field_name",
      type: "string" | "number" | "boolean" | "uuid" | "timestamp",
      generator: {
        type: "fixed" | "random_choice" | "random_string" | "random_int" | "random_float" | "random",
        // Additional properties based on generator type
        value: any,           // For fixed generators
        choices: string[],    // For random_choice
        length: number,       // For random_string
        min: number,          // For random_int/random_float
        max: number,          // For random_int/random_float
        decimals: number      // For random_float
      }
    }
  ]
}
```

## Dependencies

- `react-beautiful-dnd` - For drag-and-drop functionality
- `@monaco-editor/react` - For Python code editor with syntax highlighting
- `@radix-ui/react-*` - For UI components (dialog, select, etc.)
- `lucide-react` - For icons
- `tailwindcss` - For styling