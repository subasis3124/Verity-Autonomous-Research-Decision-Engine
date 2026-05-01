class ReportModel {
  final String id;
  final String queryId;
  final String summary;
  final Map<String, dynamic> structuredOutput;
  final DateTime createdAt;

  ReportModel({
    required this.id,
    required this.queryId,
    required this.summary,
    required this.structuredOutput,
    required this.createdAt,
  });

  factory ReportModel.fromJson(Map<String, dynamic> json) {
    return ReportModel(
      id: json['id'],
      queryId: json['query_id'],
      summary: json['summary'],
      structuredOutput: json['structured_output'] ?? {},
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
