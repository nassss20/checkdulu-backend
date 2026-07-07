<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class ScanController extends Controller
{
    public function scanUrl(Request $request)
    {
        $request->validate([
            'url' => 'required|string'
        ]);

        $targetUrl = $request->input('url');

        // --- OS DETECTION ---
        // Check if the server is running Windows or Linux
        $isWindows = strtoupper(substr(PHP_OS, 0, 3)) === 'WIN';
        
        $pythonCommand = $isWindows ? 'C:\\Python314\\python.exe' : 'python3';

        // Initialize the process
        $process = new Process([$pythonCommand, base_path('scripts/api_bridge.py'), $targetUrl]);
        $process->setTimeout(15); 

        // Only inject Windows environment variables if we are actually on Windows!
        if ($isWindows) {
            $process->setEnv([
                'SystemRoot' => 'C:\\Windows',
                'System32' => 'C:\\Windows\\System32',
                'PATH' => getenv('PATH')
            ]);
        }

        try {
            $process->mustRun();
            $output = $process->getOutput();

            $result = json_decode($output, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                return response()->json([
                    'error' => 'Failed to parse AI output.',
                    'raw_output' => $output
                ], 500);
            }

            return response()->json($result, 200);

        } catch (ProcessFailedException $exception) {
            return response()->json([
                'error' => 'CheckDulu AI Engine Execution Failed.',
                'details' => $exception->getMessage()
            ], 500);
        }
    }
}