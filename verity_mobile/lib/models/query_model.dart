class SubQuestion {
  final String id;
  final String questionText;
  final int orderIndex;

  SubQuestion({
    required this.id,
    required this.questionText,
    required this.orderIndex,
  });

  factory SubQuestion.fromJson(Map<String, dynamic> json) {
    return SubQuestion(
      id: json['id'],
      questionText: json['question_text'],
      orderIndex: json['order_index'],
    );
  }
}

class ResearchStep {
  final String id;
  final int stepNumber;
  final String llmResponse;

  ResearchStep({
    required this.id,
    required this.stepNumber,
    required this.llmResponse,
  });

  factory ResearchStep.fromJson(Map<String, dynamic> json) {
    return ResearchStep(
      id: json['id'],
      stepNumber: json['step_number'],
      llmResponse: json['llm_response'],
    );
  }
}

class QueryModel {
  final String id;
  final String rawQuery;
  final String status;
  final String? errorMessage;
  final DateTime createdAt;
  final List<SubQuestion> subQuestions;
  final List<ResearchStep> researchSteps;

  QueryModel({
    required this.id,
    required this.rawQuery,
    required this.status,
    this.errorMessage,
    required this.createdAt,
    this.subQuestions = const [],
    this.researchSteps = const [],
  });

  factory QueryModel.fromJson(Map<String, dynamic> json) {
    return QueryModel(
      id: json['id'],
      rawQuery: json['raw_query'],
      status: json['status'],
      errorMessage: json['error_message'],
      createdAt: DateTime.parse(json['created_at']),
      subQuestions: json['sub_questions'] != null 
        ? (json['sub_questions'] as List).map((i) => SubQuestion.fromJson(i)).toList()
        : [],
      researchSteps: json['research_steps'] != null 
        ? (json['research_steps'] as List).map((i) => ResearchStep.fromJson(i)).toList()
        : [],
    );
  }
}
