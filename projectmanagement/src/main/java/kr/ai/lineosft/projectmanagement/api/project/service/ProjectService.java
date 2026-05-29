package kr.ai.lineosft.projectmanagement.api.project.service;

import kr.ai.lineosft.projectmanagement.api.project.dto.ProjectRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.ProjectResponse;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import kr.ai.lineosft.projectmanagement.domain.member.repository.MemberRepository;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Project;
import kr.ai.lineosft.projectmanagement.domain.project.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ProjectService {

    private final ProjectRepository projectRepository;
    private final MemberRepository memberRepository;

    public List<ProjectResponse> getProjects() {
        return projectRepository.findAllWithMembers().stream()
                .map(ProjectResponse::new)
                .collect(Collectors.toList());
    }

    @Transactional
    public ProjectResponse createProject(ProjectRequest request, Member creator) {
        Member persistentCreator = memberRepository.findById(creator.getId())
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

        List<Member> members = new ArrayList<>();
        if (request.getMemberIds() != null && !request.getMemberIds().isEmpty()) {
            members = memberRepository.findAllById(request.getMemberIds());
        }

        Project project = Project.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .status(request.getStatus())
                .methodology(request.getMethodology())
                .progress(request.getProgress())
                .startDate(request.getStartDate())
                .endDate(request.getEndDate())
                .members(members)
                .creator(persistentCreator)
                .build();

        Project savedProject = projectRepository.save(project);
        return new ProjectResponse(savedProject);
    }

    @Transactional
    public ProjectResponse updateProject(Long id, ProjectRequest request) {
        Project project = projectRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));

        List<Member> members = new ArrayList<>();
        if (request.getMemberIds() != null && !request.getMemberIds().isEmpty()) {
            members = memberRepository.findAllById(request.getMemberIds());
        }

        project.update(
                request.getTitle(),
                request.getDescription(),
                request.getStatus(),
                request.getMethodology(),
                request.getProgress(),
                request.getStartDate(),
                request.getEndDate(),
                members
        );

        return new ProjectResponse(project);
    }

    @Transactional
    public void deleteProject(Long id) {
        Project project = projectRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));
        projectRepository.delete(project);
    }
}
