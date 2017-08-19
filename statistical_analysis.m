typing_trials = tdfread('typing_trials.csv');

%% USING rm_anova2
%wpms = typing_trials.wpm;
%participants = str2num(typing_trials.participant_id(:,2:3));
%sessions = typing_trials.session_id;
%modes = typing_trials.mode_id(:,end);
%fact_names = {'Session', 'Mode'};
%stats = rm_anova2(wpms, participants, sessions, modes, fact_names);

%% USING ranova
% Prepare data
sessions = linspace(1, 16, 16);
modes = [repmat(1, 16, 1); repmat(2, 16, 1)];
meas = table([sessions'; sessions'], modes, 'VariableNames', {'Session', 'Mode'});
typing_trials_table = struct2table(typing_trials);
wpms = typing_trials_table(:, ...
       {'participant_id', 'mode_id', 'session_id', 'wpm'});
wpms.mode_id = str2num(wpms.mode_id(:, end));
wpms.participant_id = str2num(wpms.participant_id(:, 2:end));
mean_wpms = grpstats(wpms, {'participant_id', 'mode_id', 'session_id'});
mean_wpms = sortrows(mean_wpms);
participants = [1, 2, 3, 5, 6, 7, 10, 12, 13];
participant_names = [repmat('A', length(participants), 1), ...
                     num2str(participants', '%02d')];
modes = [1, 2];
avgwpm = zeros(length(participants), 32);
for i=1:length(participants)
    participant = participants(i);
    for j=1:length(modes)
        mode = modes(j);
        for k=1:length(sessions)
            session = sessions(k);
            index = mean_wpms.participant_id == participant & ...
                    mean_wpms.mode_id == mode & ...
                    mean_wpms.session_id == session;
            avgwpm(i, (j-1) * 16 + k) = mean_wpms(index, :).mean_wpm;
        end
    end
end

% Fit repeated measures model
anova_data = array2table(avgwpm);
rm = fitrm(anova_data, 'avgwpm1-avgwpm32 ~ 1', 'WithinDesign', meas);

% Run repeated measures anova
[ranovatbl] = ranova(rm, 'WithinModel', 'Session*Mode');
ranovatbl

% make pairwise Tukey-Kramer comparisons for the two-way interactions
% see: help RepeatedMeasuresModel/multcompare
multcompare(rm, 'Mode', 'By', 'Session')
