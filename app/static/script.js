// API Base URL
const API_BASE = 'http://127.0.0.1:8000';

// Global state for auto-refresh
let autoRefreshInterval = null;
let isAutoRefreshEnabled = true;

// Global variables for enhanced functionality
let currentSortField = 'timestamp';
let currentSortDirection = 'desc';
let selectedEntries = new Set();

// Utility functions
function showLoading() {
	document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
	document.getElementById('loading-overlay').classList.add('hidden');
}

function showNotification(message, type = 'info') {
	// Create notification element
	const notification = document.createElement('div');
	notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;

	// Set colors based on type
	const colors = {
		success: 'bg-green-500 text-white',
		error: 'bg-red-500 text-white',
		warning: 'bg-yellow-500 text-white',
		info: 'bg-blue-500 text-white',
	};

	notification.className += ` ${colors[type] || colors.info}`;

	// Add icon
	const icons = {
		success: 'fas fa-check-circle',
		error: 'fas fa-exclamation-circle',
		warning: 'fas fa-exclamation-triangle',
		info: 'fas fa-info-circle',
	};

	notification.innerHTML = `
		<div class="flex items-center space-x-2">
			<i class="${icons[type] || icons.info}"></i>
			<span>${message}</span>
			<button onclick="this.parentElement.parentElement.remove()" class="ml-2 hover:opacity-75">
				<i class="fas fa-times"></i>
			</button>
		</div>
	`;

	document.body.appendChild(notification);

	// Animate in
	setTimeout(() => {
		notification.classList.remove('translate-x-full');
	}, 100);

	// Auto remove after 5 seconds
	setTimeout(() => {
		notification.classList.add('translate-x-full');
		setTimeout(() => notification.remove(), 300);
	}, 5000);
}

// Toggle auto-refresh
function toggleAutoRefresh() {
	isAutoRefreshEnabled = !isAutoRefreshEnabled;
	const button = document.getElementById('auto-refresh-toggle');

	if (isAutoRefreshEnabled) {
		button.innerHTML = '<i class="fas fa-pause mr-1"></i>Pause Auto-refresh';
		button.className =
			'bg-yellow-600 text-white px-3 py-1 rounded text-sm hover:bg-yellow-700';
		startAutoRefresh();
	} else {
		button.innerHTML = '<i class="fas fa-play mr-1"></i>Start Auto-refresh';
		button.className =
			'bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700';
		stopAutoRefresh();
	}
}

// Start auto-refresh
function startAutoRefresh() {
	if (autoRefreshInterval) {
		clearInterval(autoRefreshInterval);
	}
	autoRefreshInterval = setInterval(() => {
		if (isAutoRefreshEnabled) {
			loadDashboard();
			loadLogEntries();
		}
	}, 10000); // Refresh every 10 seconds
}

// Stop auto-refresh
function stopAutoRefresh() {
	if (autoRefreshInterval) {
		clearInterval(autoRefreshInterval);
		autoRefreshInterval = null;
	}
}

// Manual refresh all data
async function refreshAllData() {
	showLoading();
	try {
		await Promise.all([loadDashboard(), loadLogEntries()]);
		showNotification('Data refreshed successfully', 'success');
	} catch (error) {
		showNotification('Failed to refresh data', 'error');
	} finally {
		hideLoading();
	}
}

// Load dashboard data
async function loadDashboard() {
	try {
		// Load logs from SQL database
		const logsResponse = await fetch(`${API_BASE}/logs_sql`);
		console.log('logsResponse', logsResponse);
		if (!logsResponse.ok) {
			throw new Error(
				`Failed to fetch logs_sql: ${logsResponse.status} ${logsResponse.statusText}`
			);
		}
		const logs = await logsResponse.json();
		console.log('logs', logs);

		// Load log entries from SQL database
		const entriesResponse = await fetch(`${API_BASE}/log_entries_sql`);
		console.log('entriesResponse', entriesResponse);
		if (!entriesResponse.ok) {
			throw new Error(
				`Failed to fetch log_entries_sql: ${entriesResponse.status} ${entriesResponse.statusText}`
			);
		}
		const entries = await entriesResponse.json();
		console.log('entries', entries);

		// Calculate statistics from database
		const totalLogs = logs.length || 0;
		const totalEntries = entries.length || 0;
		const errorEntries =
			entries.filter((entry) => entry.level === 'ERROR').length || 0;
		const warnEntries =
			entries.filter((entry) => entry.level === 'WARN').length || 0;
		const criticalEntries =
			entries.filter((entry) => entry.level === 'CRITICAL').length || 0;

		// Update stats cards with real database data
		document.getElementById('total-logs').textContent = totalLogs;
		document.getElementById('total-incidents').textContent = totalEntries;
		document.getElementById('critical-incidents').textContent = criticalEntries;
		document.getElementById('total-categories').textContent = new Set(
			entries.map((entry) => entry.source).filter(Boolean)
		).size;

		// Update files list with SQL data
		updateFilesList(logs);

		// Update last refresh time
		updateLastRefreshTime();
	} catch (error) {
		console.error('Error loading dashboard:', error);
		showNotification(
			`Failed to load dashboard data: ${error.message}`,
			'error'
		);
	}
}

// Update last refresh time
function updateLastRefreshTime() {
	const now = new Date();
	const timeString = now.toLocaleTimeString();
	const dateString = now.toLocaleDateString();

	const lastRefreshElement = document.getElementById('last-refresh-time');
	if (lastRefreshElement) {
		lastRefreshElement.textContent = `Last updated: ${dateString} ${timeString}`;
	}
}

// Update files list
function updateFilesList(logs) {
	const container = document.getElementById('files-container');

	if (logs.length === 0) {
		container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-folder-open text-4xl mb-4"></i>
                <p>No log files uploaded yet</p>
            </div>
        `;
		return;
	}

	container.innerHTML = logs
		.map(
			(log) => `
        <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-file-alt text-blue-600"></i>
                    <div>
                        <h3 class="font-medium text-gray-900">${
													log.filename
												}</h3>
                        <p class="text-sm text-gray-500">
                            ${log.log_count || 0} entries • ${formatFileSize(
				log.size || 0
			)} • 
                            ${new Date(log.upload_time).toLocaleDateString()}
                        </p>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="px-2 py-1 text-xs rounded-full ${
											log.log_analysis_status === 'completed'
												? 'bg-green-100 text-green-800'
												: 'bg-yellow-100 text-yellow-800'
										}">
                        ${log.log_analysis_status || 'pending'}
                    </span>
                    <button class="bg-gray-200 text-gray-800 px-2 py-1 rounded text-xs hover:bg-gray-300 ml-2 details-btn" data-log-id="${
											log.id
										}">Details</button>
                    ${
											log.log_analysis_status !== 'completed'
												? `<button onclick="analyzeFile(${log.id})" 
                                class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                            Analyze
                        </button>`
												: ''
										}
                </div>
            </div>
        </div>
    `
		)
		.join('');

	// Podpinanie eventów do przycisków Details
	container.querySelectorAll('.details-btn').forEach((btn) => {
		btn.addEventListener('click', function () {
			showLogFileDetails(this.getAttribute('data-log-id'));
		});
	});
}

// File upload handling
document
	.getElementById('log-file')
	.addEventListener('change', async function (event) {
		const file = event.target.files[0];
		if (!file) return;

		const statusDiv = document.getElementById('upload-status');
		const messageSpan = document.getElementById('upload-message');

		statusDiv.classList.remove('hidden');
		messageSpan.textContent = 'Reading file...';

		try {
			// Odczytaj zawartość pliku jako tekst
			const fileContent = await file.text();

			// Przygotuj dane logu do wysłania
			const logFileData = {
				filename: file.name,
				size: file.size,
				upload_time: new Date().toISOString(),
				log_count: 0, // Zostanie zaktualizowane po analizie
				log_analysis_status: 'pending',
				analysis_result: null,
				content: fileContent,
			};

			// Wyślij log do backendu
			const logFileResponse = await fetch(`${API_BASE}/logs_sql`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(logFileData),
			});

			if (!logFileResponse.ok) {
				throw new Error(
					`Failed to create log file entry: ${logFileResponse.statusText}`
				);
			}

			messageSpan.textContent = 'Log file uploaded successfully!';
			setTimeout(() => statusDiv.classList.add('hidden'), 2000);
			// Odśwież dashboard
			loadDashboard();
			loadLogEntries();
		} catch (error) {
			console.error('Upload error:', error);
			messageSpan.textContent = `Upload failed: ${error.message}`;
			setTimeout(() => statusDiv.classList.add('hidden'), 3000);
		}
	});

// Parse log line and create log entry object
function parseLogLine(line, logFileId) {
	try {
		// Basic log parsing - you can enhance this with more sophisticated patterns
		const timestamp = new Date().toISOString();
		let level = 'INFO';
		let message = line;
		let source = 'unknown';
		let functionName = null;
		let lineNumber = null;

		// Try to extract log level from common patterns
		const levelPatterns = [
			/\[?(CRITICAL|ERROR|WARN|WARNING|INFO|DEBUG)\]?/i,
			/(CRITICAL|ERROR|WARN|WARNING|INFO|DEBUG):/i,
			/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(CRITICAL|ERROR|WARN|WARNING|INFO|DEBUG)\]/i,
		];

		for (const pattern of levelPatterns) {
			const match = line.match(pattern);
			if (match) {
				level = match[1] || match[2];
				message = line.replace(pattern, '').trim();
				break;
			}
		}

		// Try to extract timestamp
		const timestampPattern =
			/(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)/;
		const timestampMatch = line.match(timestampPattern);
		if (timestampMatch) {
			message = line.replace(timestampMatch[0], '').trim();
		}

		// Try to extract source/function information
		const sourcePattern = /\[([^\]]+)\]/g;
		const sourceMatches = [...line.matchAll(sourcePattern)];
		if (sourceMatches.length > 0) {
			source = sourceMatches[0][1];
		}

		return {
			log_file_id: logFileId,
			timestamp: timestamp,
			level: level.toUpperCase(),
			message: message || line,
			source: source,
			line_number: lineNumber,
			function_name: functionName,
		};
	} catch (error) {
		console.warn('Failed to parse log line:', line, error);
		return null;
	}
}

// Analyze file
async function analyzeFile(logId) {
	showLoading();

	try {
		// Get log file details
		const logResponse = await fetch(`${API_BASE}/logs_sql/${logId}`);
		if (!logResponse.ok) {
			throw new Error(`Failed to get log file: ${logResponse.statusText}`);
		}
		const logFile = await logResponse.json();

		// Use full raw log content for analysis
		const analysisPrompt = `You are an expert DevOps engineer. Analyze the following log file and stack trace. Identify the root cause, point to the exact line or function if possible, and propose a concrete solution. If the error is related to a known library or framework, suggest a fix or workaround.\n\nLog file content:\n${logFile.content}`;

		if (!logFile.content || !logFile.content.trim()) {
			showNotification('No log content to analyze for this file.', 'warning');
			hideLoading();
			return;
		}

		// Send for AI analysis
		const analysisResponse = await fetch(`${API_BASE}/analyze`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ log: analysisPrompt }),
		});

		if (!analysisResponse.ok) {
			throw new Error(`Analysis failed: ${analysisResponse.statusText}`);
		}

		const analysisResult = await analysisResponse.json();

		// Update log file with analysis result
		await fetch(`${API_BASE}/logs_sql/${logId}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				id: logFile.id,
				filename: logFile.filename,
				size: logFile.size,
				upload_time:
					typeof logFile.upload_time === 'string'
						? logFile.upload_time
						: new Date(logFile.upload_time).toISOString(),
				log_count: logFile.log_count,
				log_analysis_status: 'completed',
				analysis_result: analysisResult.analysis,
				content: logFile.content || null,
			}),
		});

		showNotification('Analysis completed successfully!', 'success');

		// Reload dashboard and log entries
		loadDashboard();
		loadLogEntries();
	} catch (error) {
		console.error('Analysis error:', error);
		showNotification(`Analysis failed: ${error.message}`, 'error');
	} finally {
		hideLoading();
	}
}

// Search incidents
async function searchIncidents() {
	const query = document.getElementById('search-query').value.trim();
	const topK = document.getElementById('top-k').value;
	const threshold = document.getElementById('similarity-threshold').value;

	if (!query) {
		showNotification('Please enter a search query', 'warning');
		return;
	}

	showLoading();

	try {
		const url = `${API_BASE}/vector/search?query=${encodeURIComponent(
			query
		)}&top_k=${topK}&similarity_threshold=${threshold}`;
		const response = await fetch(url);

		if (!response.ok) {
			throw new Error(`Search failed: ${response.statusText}`);
		}

		const result = await response.json();
		displaySearchResults(result);
	} catch (error) {
		console.error('Search error:', error);
		showNotification(`Search failed: ${error.message}`, 'error');
	} finally {
		hideLoading();
	}
}

// Display search results
function displaySearchResults(result) {
	const container = document.getElementById('results-container');
	const section = document.getElementById('results-section');

	if (result.results.length === 0) {
		container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-search text-4xl mb-4"></i>
                <p>No similar incidents found</p>
                <p class="text-sm">Try adjusting the similarity threshold or search query</p>
            </div>
        `;
	} else {
		container.innerHTML = `
            <div class="mb-4">
                <p class="text-sm text-gray-600">
                    Found ${
											result.total_found
										} similar incidents for: <strong>"${result.query}"</strong>
                </p>
            </div>
            ${result.results
							.map(
								(incident) => `
                <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center space-x-3">
                            <span class="px-2 py-1 text-xs rounded-full ${
															incident.severity === 'critical'
																? 'bg-red-100 text-red-800'
																: incident.severity === 'high'
																? 'bg-orange-100 text-orange-800'
																: incident.severity === 'medium'
																? 'bg-yellow-100 text-yellow-800'
																: 'bg-green-100 text-green-800'
														}">
                                ${incident.severity}
                            </span>
                            <span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                                ${incident.category}
                            </span>
                            <span class="text-sm text-gray-500">
                                ${Math.round(
																	incident.similarity_score * 100
																)}% similar
                            </span>
                        </div>
                        <span class="text-xs text-gray-400">
                            ${new Date(incident.timestamp).toLocaleString()}
                        </span>
                    </div>
                    
                    <div class="mb-3">
                        <h4 class="font-medium text-gray-900 mb-2">Log Content:</h4>
                        <div class="bg-gray-100 p-3 rounded text-sm font-mono text-gray-700">
                            ${incident.log_content}
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">AI Analysis:</h4>
                        <div class="bg-blue-50 p-3 rounded text-sm text-gray-700 markdown-output" id="analysis-md-${
													incident.incident_id
												}"></div>
                    </div>
                    
                    <div class="mt-3 text-xs text-gray-500">
                        Source: ${incident.source_file} | ID: ${
									incident.incident_id
								}
                    </div>
                </div>
            `
							)
							.join('')}
        `;
	}

	section.classList.remove('hidden');
	section.scrollIntoView({ behavior: 'smooth' });

	// Render markdown for each analysis
	if (result.results && result.results.length > 0) {
		result.results.forEach((incident) => {
			const el = document.getElementById(`analysis-md-${incident.incident_id}`);
			if (el) {
				el.innerHTML = marked.parse(incident.analysis || '');
			}
		});
	}
}

// Utility function to format file size
function formatFileSize(bytes) {
	if (bytes === 0) return '0 Bytes';
	const k = 1024;
	const sizes = ['Bytes', 'KB', 'MB', 'GB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));
	return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Load log entries and display in table
async function loadLogEntries() {
	try {
		const response = await fetch(`${API_BASE}/log_entries_sql`);
		const entries = await response.json();

		// Store entries globally for filtering
		window.allLogEntries = entries;
		window.currentPage = 1;
		window.entriesPerPage = 20;

		// Populate source filter
		populateSourceFilter(entries);

		// Apply current filters
		filterEntries();
	} catch (error) {
		console.error('Error loading log entries:', error);
		showNotification('Failed to load log entries', 'error');
	}
}

// Populate source filter dropdown
function populateSourceFilter(entries) {
	const sourceFilter = document.getElementById('source-filter');
	const sources = [
		...new Set(entries.map((entry) => entry.source).filter(Boolean)),
	].sort();

	// Clear existing options except "All Sources"
	sourceFilter.innerHTML = '<option value="">All Sources</option>';

	// Add source options
	sources.forEach((source) => {
		const option = document.createElement('option');
		option.value = source;
		option.textContent = source;
		sourceFilter.appendChild(option);
	});
}

// Display log entries in table with pagination
function displayLogEntries(entries) {
	const tableBody = document.getElementById('log-entries-table');
	const startIndex = (window.currentPage - 1) * window.entriesPerPage;
	const endIndex = startIndex + window.entriesPerPage;
	const pageEntries = entries.slice(startIndex, endIndex);

	// Update pagination info
	document.getElementById('entries-start').textContent =
		entries.length > 0 ? startIndex + 1 : 0;
	document.getElementById('entries-end').textContent = Math.min(
		endIndex,
		entries.length
	);
	document.getElementById('entries-total').textContent = entries.length;
	document.getElementById(
		'current-page'
	).textContent = `Page ${window.currentPage}`;

	// Update pagination buttons
	document.getElementById('prev-page').disabled = window.currentPage <= 1;
	document.getElementById('next-page').disabled = endIndex >= entries.length;

	// Update filter summary
	updateFilterSummary(entries);

	if (pageEntries.length === 0) {
		tableBody.innerHTML = `
			<tr>
				<td colspan="7" class="px-6 py-4 text-center text-gray-500">
					<i class="fas fa-inbox text-2xl mb-2"></i>
					<p>No log entries found</p>
				</td>
			</tr>
		`;
		return;
	}

	tableBody.innerHTML = pageEntries
		.map(
			(entry) => `
		<tr class="hover:bg-gray-50">
			<td class="px-6 py-4 whitespace-nowrap">
				<input type="checkbox" class="entry-checkbox rounded border-gray-300" 
					   value="${entry.id}" onchange="toggleEntrySelection(${entry.id})">
			</td>
			<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
				${new Date(entry.timestamp).toLocaleString()}
			</td>
			<td class="px-6 py-4 whitespace-nowrap">
				<span class="px-2 py-1 text-xs rounded-full ${
					entry.level === 'CRITICAL'
						? 'bg-red-100 text-red-800'
						: entry.level === 'ERROR'
						? 'bg-red-100 text-red-800'
						: entry.level === 'WARN'
						? 'bg-yellow-100 text-yellow-800'
						: entry.level === 'INFO'
						? 'bg-blue-100 text-blue-800'
						: 'bg-gray-100 text-gray-800'
				}">
					${entry.level || 'UNKNOWN'}
				</span>
			</td>
			<td class="px-6 py-4 text-sm text-gray-900 max-w-md truncate" title="${
				entry.message || ''
			}">
				${entry.message || 'No message'}
			</td>
			<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
				${entry.source || '-'}
			</td>
			<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
				${entry.function_name || '-'}
			</td>
			<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
				${entry.line_number || '-'}
			</td>
		</tr>
	`
		)
		.join('');

	// Update checkboxes state
	updateCheckboxStates();
}

// Update filter summary
function updateFilterSummary(entries) {
	const summaryDiv = document.getElementById('filter-summary');
	const filterText = document.getElementById('filter-text');
	const filterCount = document.getElementById('filter-count');

	const levelFilter = document.getElementById('level-filter').value;
	const messageSearch = document.getElementById('message-search').value;
	const sourceFilter = document.getElementById('source-filter').value;
	const dateFrom = document.getElementById('date-from').value;
	const dateTo = document.getElementById('date-to').value;

	const hasFilters =
		levelFilter || messageSearch || sourceFilter || dateFrom || dateTo;

	if (hasFilters) {
		const filters = [];
		if (levelFilter) filters.push(`Level: ${levelFilter}`);
		if (messageSearch) filters.push(`Message: "${messageSearch}"`);
		if (sourceFilter) filters.push(`Source: ${sourceFilter}`);
		if (dateFrom || dateTo) {
			const dateRange = `${dateFrom || 'any'} to ${dateTo || 'any'}`;
			filters.push(`Date: ${dateRange}`);
		}

		filterText.textContent = filters.join(', ');
		filterCount.textContent = `(${entries.length} results)`;
		summaryDiv.classList.remove('hidden');
	} else {
		summaryDiv.classList.add('hidden');
	}
}

// Filter log entries
function filterEntries() {
	const levelFilter = document.getElementById('level-filter').value;
	const messageSearch = document
		.getElementById('message-search')
		.value.toLowerCase();
	const sourceFilter = document.getElementById('source-filter').value;
	const dateFrom = document.getElementById('date-from').value;
	const dateTo = document.getElementById('date-to').value;

	let filteredEntries = window.allLogEntries || [];

	// Filter by level
	if (levelFilter) {
		filteredEntries = filteredEntries.filter(
			(entry) => entry.level === levelFilter
		);
	}

	// Filter by message content
	if (messageSearch) {
		filteredEntries = filteredEntries.filter((entry) =>
			(entry.message || '').toLowerCase().includes(messageSearch)
		);
	}

	// Filter by source
	if (sourceFilter) {
		filteredEntries = filteredEntries.filter(
			(entry) => entry.source === sourceFilter
		);
	}

	// Filter by date range
	if (dateFrom || dateTo) {
		filteredEntries = filteredEntries.filter((entry) => {
			const entryDate = new Date(entry.timestamp).toISOString().split('T')[0];
			if (dateFrom && entryDate < dateFrom) return false;
			if (dateTo && entryDate > dateTo) return false;
			return true;
		});
	}

	// Apply sorting
	filteredEntries = sortEntries(filteredEntries);

	// Reset to first page when filtering
	window.currentPage = 1;
	displayLogEntries(filteredEntries);
}

// Sort entries
function sortEntries(entries) {
	return entries.sort((a, b) => {
		let aVal = a[currentSortField];
		let bVal = b[currentSortField];

		// Handle timestamp sorting
		if (currentSortField === 'timestamp') {
			aVal = new Date(aVal);
			bVal = new Date(bVal);
		}

		// Handle string sorting
		if (typeof aVal === 'string') {
			aVal = aVal.toLowerCase();
			bVal = bVal.toLowerCase();
		}

		if (currentSortDirection === 'asc') {
			return aVal > bVal ? 1 : -1;
		} else {
			return aVal < bVal ? 1 : -1;
		}
	});
}

// Sort table
function sortTable(field) {
	if (currentSortField === field) {
		currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
	} else {
		currentSortField = field;
		currentSortDirection = 'asc';
	}

	filterEntries();
}

// Clear all filters
function clearFilters() {
	document.getElementById('level-filter').value = '';
	document.getElementById('message-search').value = '';
	document.getElementById('source-filter').value = '';
	document.getElementById('date-from').value = '';
	document.getElementById('date-to').value = '';

	filterEntries();
}

// Toggle entry selection
function toggleEntrySelection(entryId) {
	if (selectedEntries.has(entryId)) {
		selectedEntries.delete(entryId);
	} else {
		selectedEntries.add(entryId);
	}

	updateBulkActions();
	updateCheckboxStates();
}

// Update checkbox states
function updateCheckboxStates() {
	const selectAllCheckbox = document.getElementById('select-all');
	const entryCheckboxes = document.querySelectorAll('.entry-checkbox');

	// Update select all checkbox
	const checkedCount = entryCheckboxes.length;
	const selectedCount = Array.from(entryCheckboxes).filter(
		(cb) => cb.checked
	).length;

	selectAllCheckbox.checked =
		selectedCount === checkedCount && checkedCount > 0;
	selectAllCheckbox.indeterminate =
		selectedCount > 0 && selectedCount < checkedCount;

	// Update individual checkboxes
	entryCheckboxes.forEach((checkbox) => {
		const entryId = parseInt(checkbox.value);
		checkbox.checked = selectedEntries.has(entryId);
	});
}

// Update bulk actions visibility
function updateBulkActions() {
	const bulkActionsDiv = document.getElementById('bulk-actions');
	const selectedCountSpan = document.getElementById('selected-count');

	if (selectedEntries.size > 0) {
		bulkActionsDiv.classList.remove('hidden');
		selectedCountSpan.textContent = selectedEntries.size;
	} else {
		bulkActionsDiv.classList.add('hidden');
	}
}

// Select all entries
function selectAllEntries() {
	const selectAllCheckbox = document.getElementById('select-all');
	const entryCheckboxes = document.querySelectorAll('.entry-checkbox');

	if (selectAllCheckbox.checked) {
		entryCheckboxes.forEach((checkbox) => {
			selectedEntries.add(parseInt(checkbox.value));
		});
	} else {
		selectedEntries.clear();
	}

	updateBulkActions();
	updateCheckboxStates();
}

// Export to CSV
function exportToCSV() {
	const entries = getCurrentFilteredEntries();
	if (entries.length === 0) {
		showNotification('No entries to export', 'warning');
		return;
	}

	const csvContent = generateCSV(entries);
	downloadFile(csvContent, 'log_entries.csv', 'text/csv');
	showNotification(`Exported ${entries.length} entries to CSV`, 'success');
}

// Export to JSON
function exportToJSON() {
	const entries = getCurrentFilteredEntries();
	if (entries.length === 0) {
		showNotification('No entries to export', 'warning');
		return;
	}

	const jsonContent = JSON.stringify(entries, null, 2);
	downloadFile(jsonContent, 'log_entries.json', 'application/json');
	showNotification(`Exported ${entries.length} entries to JSON`, 'success');
}

// Export selected entries
function exportSelected() {
	if (selectedEntries.size === 0) {
		showNotification('No entries selected', 'warning');
		return;
	}

	const selectedEntriesList = Array.from(selectedEntries);
	const entries = window.allLogEntries.filter((entry) =>
		selectedEntriesList.includes(entry.id)
	);

	const csvContent = generateCSV(entries);
	downloadFile(csvContent, 'selected_log_entries.csv', 'text/csv');
	showNotification(
		`Exported ${entries.length} selected entries to CSV`,
		'success'
	);
}

// Generate CSV content
function generateCSV(entries) {
	const headers = [
		'Timestamp',
		'Level',
		'Message',
		'Source',
		'Function',
		'Line',
	];
	const csvRows = [headers.join(',')];

	entries.forEach((entry) => {
		const row = [
			new Date(entry.timestamp).toLocaleString(),
			entry.level || '',
			`"${(entry.message || '').replace(/"/g, '""')}"`,
			entry.source || '',
			entry.function_name || '',
			entry.line_number || '',
		];
		csvRows.push(row.join(','));
	});

	return csvRows.join('\n');
}

// Download file
function downloadFile(content, filename, contentType) {
	const blob = new Blob([content], { type: contentType });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
}

// Get current filtered entries
function getCurrentFilteredEntries() {
	const levelFilter = document.getElementById('level-filter').value;
	const messageSearch = document
		.getElementById('message-search')
		.value.toLowerCase();
	const sourceFilter = document.getElementById('source-filter').value;
	const dateFrom = document.getElementById('date-from').value;
	const dateTo = document.getElementById('date-to').value;

	let filteredEntries = window.allLogEntries || [];

	if (levelFilter) {
		filteredEntries = filteredEntries.filter(
			(entry) => entry.level === levelFilter
		);
	}
	if (messageSearch) {
		filteredEntries = filteredEntries.filter((entry) =>
			(entry.message || '').toLowerCase().includes(messageSearch)
		);
	}
	if (sourceFilter) {
		filteredEntries = filteredEntries.filter(
			(entry) => entry.source === sourceFilter
		);
	}
	if (dateFrom || dateTo) {
		filteredEntries = filteredEntries.filter((entry) => {
			const entryDate = new Date(entry.timestamp).toISOString().split('T')[0];
			if (dateFrom && entryDate < dateFrom) return false;
			if (dateTo && entryDate > dateTo) return false;
			return true;
		});
	}

	return sortEntries(filteredEntries);
}

// Delete selected entries
async function deleteSelected() {
	if (selectedEntries.size === 0) {
		showNotification('No entries selected', 'warning');
		return;
	}

	if (
		!confirm(
			`Are you sure you want to delete ${selectedEntries.size} selected entries?`
		)
	) {
		return;
	}

	showLoading();

	try {
		const deletePromises = Array.from(selectedEntries).map((entryId) =>
			fetch(`${API_BASE}/log_entries_sql/${entryId}`, {
				method: 'DELETE',
			})
		);

		await Promise.all(deletePromises);

		selectedEntries.clear();
		updateBulkActions();

		showNotification(
			`Successfully deleted ${deletePromises.length} entries`,
			'success'
		);

		// Reload data
		loadDashboard();
		loadLogEntries();
	} catch (error) {
		console.error('Delete error:', error);
		showNotification('Failed to delete entries', 'error');
	} finally {
		hideLoading();
	}
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function () {
	loadDashboard();
	loadLogEntries(); // Load log entries on page load
	startAutoRefresh(); // Start auto-refresh

	// Add keyboard shortcut for search
	document
		.getElementById('search-query')
		.addEventListener('keypress', function (event) {
			if (event.key === 'Enter') {
				searchIncidents();
			}
		});

	// Add event listeners for log entries filtering
	document
		.getElementById('level-filter')
		.addEventListener('change', filterEntries);
	document
		.getElementById('message-search')
		.addEventListener('input', filterEntries);
	document
		.getElementById('source-filter')
		.addEventListener('change', filterEntries);
	document
		.getElementById('date-from')
		.addEventListener('change', filterEntries);
	document.getElementById('date-to').addEventListener('change', filterEntries);

	// Add event listener for select all checkbox
	document
		.getElementById('select-all')
		.addEventListener('change', selectAllEntries);

	// Add keyboard shortcuts
	document.addEventListener('keydown', function (event) {
		// Ctrl+R to refresh
		if (event.ctrlKey && event.key === 'r') {
			event.preventDefault();
			refreshAllData();
		}
		// Ctrl+Shift+R to toggle auto-refresh
		if (event.ctrlKey && event.shiftKey && event.key === 'R') {
			event.preventDefault();
			toggleAutoRefresh();
		}
		// Ctrl+A to select all
		if (event.ctrlKey && event.key === 'a') {
			event.preventDefault();
			selectAllEntries();
		}
	});

	// Setup modal close events after DOM is loaded
	setupModalCloseEvents();
});

// Clean up on page unload
window.addEventListener('beforeunload', function () {
	stopAutoRefresh();
});

// Function to show log file details
async function showLogFileDetails(logId) {
	try {
		const response = await fetch(`${API_BASE}/logs_sql/${logId}`);
		if (!response.ok) {
			showNotification('Failed to fetch log file details', 'error');
			return;
		}
		const log = await response.json();
		document.getElementById('log-details-filename').textContent = log.filename;
		document.getElementById('log-details-upload-time').textContent = new Date(
			log.upload_time
		).toLocaleString();
		document.getElementById('log-details-count').textContent = log.log_count;
		document.getElementById('log-details-status').textContent =
			log.log_analysis_status;
		// Render markdown if possible, fallback to plain text
		const analysisDiv = document.getElementById('log-details-analysis');
		if (log.analysis_result) {
			if (window.marked) {
				try {
					analysisDiv.innerHTML = marked.parse(log.analysis_result.trim());
				} catch (err) {
					analysisDiv.innerText = log.analysis_result;
				}
			} else {
				analysisDiv.innerText = log.analysis_result;
			}
		} else {
			analysisDiv.innerHTML =
				'<span class="text-gray-400">No AI analysis available</span>';
		}
		document
			.getElementById('log-details-modal-overlay')
			.classList.remove('hidden');
	} catch (err) {
		console.error('Error in showLogFileDetails:', err);
		showNotification('JS error: ' + err.message, 'error');
	}
}

function closeLogFileDetails() {
	console.log('Modal closed');
	document.getElementById('log-details-modal-overlay').classList.add('hidden');
}

// Add modal close on overlay click and Esc key
function setupModalCloseEvents() {
	const overlay = document.getElementById('log-details-modal-overlay');
	const modal = document.getElementById('log-details-modal');
	if (!overlay || !modal) return;

	overlay.addEventListener('click', function (e) {
		if (e.target === overlay) {
			closeLogFileDetails();
		}
	});
	document.addEventListener('keydown', function (e) {
		if (!overlay.classList.contains('hidden') && e.key === 'Escape') {
			closeLogFileDetails();
		}
	});
}

window.showLogFileDetails = showLogFileDetails;
