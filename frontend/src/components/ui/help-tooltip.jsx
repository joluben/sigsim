import { Button } from '@/components/ui/button';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';

const HelpTooltip = ({
    content,
    type = 'info',
    side = 'top',
    className = "",
    children
}) => {
    const getIcon = () => {
        switch (type) {
            case 'success':
                return <CheckCircleIcon className="h-4 w-4 text-green-600" />;
            case 'warning':
                return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-600" />;
            case 'error':
                return <XCircleIcon className="h-4 w-4 text-red-600" />;
            default:
                return <InformationCircleIcon className="h-4 w-4 text-blue-600" />;
        }
    };

    const getContentStyle = () => {
        switch (type) {
            case 'success':
                return 'border-green-200 bg-green-50 text-green-800';
            case 'warning':
                return 'border-yellow-200 bg-yellow-50 text-yellow-800';
            case 'error':
                return 'border-red-200 bg-red-50 text-red-800';
            default:
                return 'border-blue-200 bg-blue-50 text-blue-800';
        }
    };

    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    {children || (
                        <Button
                            variant="ghost"
                            size="sm"
                            className={`h-4 w-4 p-0 hover:bg-transparent ${className}`}
                        >
                            {getIcon()}
                        </Button>
                    )}
                </TooltipTrigger>
                <TooltipContent
                    side={side}
                    className={`max-w-xs border ${getContentStyle()}`}
                >
                    <p className="text-sm">{content}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

export default HelpTooltip;