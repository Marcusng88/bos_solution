"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download, FileText, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface PDFDownloadButtonProps {
  htmlContent?: string;
  jsonData?: any;
  reportType?: "html" | "json" | "roi";
  filename?: string;
  className?: string;
  disabled?: boolean;
}

export function PDFDownloadButton({
  htmlContent,
  jsonData,
  reportType = "html",
  filename,
  className = "",
  disabled = false
}: PDFDownloadButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const downloadPDF = async () => {
    if (!htmlContent && !jsonData) {
      toast({
        title: "No content available",
        description: "Please generate a report first before downloading as PDF.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      let endpoint = "";
      let body: any = {};

      switch (reportType) {
        case "html":
          endpoint = "/api/pdf/convert-html-to-pdf";
          body = {
            html_content: htmlContent,
            filename: filename
          };
          break;
        case "json":
          endpoint = "/api/pdf/convert-json-to-pdf";
          body = {
            json_data: jsonData,
            filename: filename
          };
          break;
        case "roi":
          endpoint = "/api/pdf/roi-report-to-pdf";
          body = {
            report_data: jsonData,
            filename: filename
          };
          break;
        default:
          throw new Error("Invalid report type");
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get the PDF blob
      const pdfBlob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename || `roi_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: "PDF Downloaded",
        description: "Your ROI report has been successfully downloaded as PDF.",
      });

    } catch (error) {
      console.error("PDF download error:", error);
      toast({
        title: "Download Failed",
        description: "Failed to download PDF. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      onClick={downloadPDF}
      disabled={disabled || isLoading || (!htmlContent && !jsonData)}
      className={`${className}`}
      variant="outline"
    >
      {isLoading ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : (
        <Download className="mr-2 h-4 w-4" />
      )}
      {isLoading ? "Generating PDF..." : "Download PDF"}
    </Button>
  );
}

interface PDFPreviewButtonProps {
  htmlContent?: string;
  jsonData?: any;
  reportType?: "html" | "json" | "roi";
  filename?: string;
  className?: string;
  disabled?: boolean;
}

export function PDFPreviewButton({
  htmlContent,
  jsonData,
  reportType = "html",
  filename,
  className = "",
  disabled = false
}: PDFPreviewButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const previewPDF = async () => {
    if (!htmlContent && !jsonData) {
      toast({
        title: "No content available",
        description: "Please generate a report first before previewing as PDF.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      let endpoint = "";
      let body: any = {};

      switch (reportType) {
        case "html":
          endpoint = "/api/pdf/convert-html-to-pdf";
          body = {
            html_content: htmlContent,
            filename: filename
          };
          break;
        case "json":
          endpoint = "/api/pdf/convert-json-to-pdf";
          body = {
            json_data: jsonData,
            filename: filename
          };
          break;
        case "roi":
          endpoint = "/api/pdf/roi-report-to-pdf";
          body = {
            report_data: jsonData,
            filename: filename
          };
          break;
        default:
          throw new Error("Invalid report type");
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get the PDF blob
      const pdfBlob = await response.blob();
      
      // Create URL for preview
      const url = window.URL.createObjectURL(pdfBlob);
      
      // Open PDF in new tab
      window.open(url, '_blank');

      toast({
        title: "PDF Preview",
        description: "PDF report opened in new tab for preview.",
      });

    } catch (error) {
      console.error("PDF preview error:", error);
      toast({
        title: "Preview Failed",
        description: "Failed to preview PDF. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      onClick={previewPDF}
      disabled={disabled || isLoading || (!htmlContent && !jsonData)}
      className={`${className}`}
      variant="ghost"
    >
      {isLoading ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : (
        <FileText className="mr-2 h-4 w-4" />
      )}
      {isLoading ? "Generating Preview..." : "Preview PDF"}
    </Button>
  );
}

interface PDFConversionStatusProps {
  isConverting: boolean;
  conversionProgress?: number;
  className?: string;
}

export function PDFConversionStatus({
  isConverting,
  conversionProgress,
  className = ""
}: PDFConversionStatusProps) {
  if (!isConverting) return null;

  return (
    <div className={`flex items-center space-x-2 p-4 bg-blue-50 border border-blue-200 rounded-lg ${className}`}>
      <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
      <div className="flex-1">
        <p className="text-sm font-medium text-blue-900">
          Converting to PDF...
        </p>
        {conversionProgress !== undefined && (
          <div className="w-full bg-blue-200 rounded-full h-2 mt-1">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${conversionProgress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
