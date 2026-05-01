class UserModel {
  final String id;
  final String email;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
