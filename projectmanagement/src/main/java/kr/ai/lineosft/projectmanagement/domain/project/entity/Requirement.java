package kr.ai.lineosft.projectmanagement.domain.project.entity;

import jakarta.persistence.*;
import kr.ai.lineosft.projectmanagement.common.entity.BaseTimeEntity;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "requirements")
public class Requirement extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String requirementCode; // Global unique code e.g., REQ-00001

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private RequirementCategory category;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RequirementPriority priority;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RequirementStatus status;

    @Column(nullable = false)
    private Integer progress;

    private String requestedBy;

    private String domainName;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Member author;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assignee_id")
    private Member assignee;

    @OneToMany(mappedBy = "requirement")
    private List<Task> tasks = new ArrayList<>();

    @Builder
    private Requirement(String requirementCode, String title, String description, RequirementCategory category,
                        RequirementPriority priority, RequirementStatus status, Integer progress,
                        Project project, Member author, Member assignee, String requestedBy, String domainName) {
        this.requirementCode = requirementCode;
        this.title = title;
        this.description = description;
        this.category = category;
        this.priority = priority != null ? priority : RequirementPriority.MEDIUM;
        this.status = status != null ? status : RequirementStatus.DRAFT;
        this.progress = progress != null ? progress : 0;
        this.project = project;
        this.author = author;
        this.assignee = assignee;
        this.requestedBy = requestedBy;
        this.domainName = domainName;
    }

    public void update(String title, String description, RequirementCategory category,
                       RequirementPriority priority, RequirementStatus status, Integer progress, Member assignee,
                       String requestedBy, String domainName) {
        this.title = title;
        this.description = description;
        this.category = category;
        this.priority = priority;
        this.status = status;
        if (progress != null && progress >= 0 && progress <= 100) {
            this.progress = progress;
        }
        this.assignee = assignee;
        this.requestedBy = requestedBy;
        this.domainName = domainName;
    }

    public void updateProgress(Integer progress) {
        if (progress != null && progress >= 0 && progress <= 100) {
            this.progress = progress;
        }
    }

    public void updateStatus(RequirementStatus status) {
        if (status != null) {
            this.status = status;
        }
    }

    public void setRequirementCode(String requirementCode) {
        this.requirementCode = requirementCode;
    }
}
