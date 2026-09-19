"""initial_schema

Revision ID: 367b5453b454
Revises: 
Create Date: 2026-09-19 13:57:21.926296+00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '367b5453b454'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), server_default='user', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='QUESTION_PAPER', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='QUEUED', nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_pages', sa.Integer(), server_default='1', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_status'), 'documents', ['status'], unique=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)

    # 3. document_relationships table
    op.create_table(
        'document_relationships',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('parent_document_id', sa.String(length=36), nullable=False),
        sa.Column('related_document_id', sa.String(length=36), nullable=False),
        sa.Column('relation_type', sa.String(length=50), server_default='ANSWER_KEY_FOR', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['parent_document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_relationships_parent_document_id'), 'document_relationships', ['parent_document_id'], unique=False)
    op.create_index(op.f('ix_document_relationships_related_document_id'), 'document_relationships', ['related_document_id'], unique=False)

    # 4. questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('question_number', sa.String(length=50), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), server_default='multiple_choice', nullable=False),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('answer', sa.String(length=255), nullable=True),
        sa.Column('answer_explanation', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('review_required', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('review_reasons', sa.JSON(), nullable=False),
        sa.Column('source_pages', sa.JSON(), nullable=False),
        sa.Column('bounding_box', sa.JSON(), nullable=True),
        sa.Column('has_diagram_or_table', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('raw_extracted_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_document_id'), 'questions', ['document_id'], unique=False)
    op.create_index(op.f('ix_questions_question_number'), 'questions', ['question_number'], unique=False)
    op.create_index(op.f('ix_questions_review_required'), 'questions', ['review_required'], unique=False)

    # 5. answer_keys table
    op.create_table(
        'answer_keys',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('raw_key_data', sa.JSON(), nullable=False),
        sa.Column('detection_confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('is_associated', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answer_keys_document_id'), 'answer_keys', ['document_id'], unique=False)

def downgrade() -> None:
    op.drop_table('answer_keys')
    op.drop_table('questions')
    op.drop_table('document_relationships')
    op.drop_table('documents')
    op.drop_table('users')
